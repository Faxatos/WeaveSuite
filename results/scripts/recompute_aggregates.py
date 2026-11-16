#!/usr/bin/env python3
"""Recompute every aggregate reported in the thesis and in the HUGS 2027 article from the files in results/.

Usage (from the repository root or from results/):
    python results/scripts/recompute_aggregates.py              # per-run values of manifest.csv (the values
                                                                #   recorded for the thesis)
    python results/scripts/recompute_aggregates.py --from-files # per-run values from each run's summary.json
    python results/scripts/recompute_aggregates.py --from-raw   # coverage from the JaCoCo XML files and
                                                                #   mutation score from mutation/mutants.json
    python results/scripts/recompute_aggregates.py --csv out.csv
Only the Python 3 standard library is needed. The script reads the data; it never modifies it.

Each line shows: where the value is reported, the runs it is computed on, the statistic, the reported value,
the value recomputed here, and "same" when they agree at the printed precision. "n" is the number of runs
with values for that configuration.
"""
import argparse, csv, json, math, os, statistics, sys
import xml.etree.ElementTree as ET

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.dirname(SCRIPTS)
REPO = os.path.dirname(RESULTS)
# Killable mutants (upper bound of the mutation score, thesis Sec. 4.5.3 and 5.1.1): killed / total
KILLABLE = {'sockshop': (32, 37), 'kubepay': (24, 27), 'lakeside-mutual': (25, 32)}


def from_manifest(row):
    svc = {}
    for part in filter(None, row['coverage_per_service'].split(';')):
        k, v = part.split('='); svc[k] = float(v)
    # pass rate and mutation score from the integer counts (exact), coverage as recorded
    return dict(row, present=True, pass_rate=100 * int(row['passed']) / int(row['tests']),
                cov=float(row['instruction_coverage']),
                mut=100 * int(row['killed']) / int(row['total_mutants']), killed=int(row['killed']),
                total_mutants=int(row['total_mutants']),
                total_instr=int(row['total_instructions']), svc=svc, source='manifest.csv')


def load_runs(source):
    runs = []
    with open(os.path.join(RESULTS, 'manifest.csv'), encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            if source == 'manifest':
                runs.append(from_manifest(row) if row['instruction_coverage'] else dict(row, present=False)); continue
            if not row['path']:
                runs.append(dict(row, present=False)); continue
            from_raw = source == 'raw'
            d = os.path.join(REPO, row['path'])
            s = json.load(open(os.path.join(d, 'summary.json'), encoding='utf-8'))
            r = dict(row, present=True, pass_rate=s['pass_rate'] * 100, cov=s['coverage'] * 100,
                     mut=s['mutation_score'] * 100, killed=s['killed'], total_mutants=s['total_mutants'],
                     total_instr=s['coverage_per_service'].get('_total'),
                     svc={k: v * 100 for k, v in s['coverage_per_service'].items() if not k.startswith('_')},
                     source='summary.json')
            if from_raw:
                cov_dir, mp = os.path.join(d, 'coverage'), os.path.join(d, 'mutation', 'mutants.json')
                xs = sorted(f for f in os.listdir(cov_dir) if f.endswith('.xml')) if os.path.isdir(cov_dir) else []
                if xs:
                    cv = tt = 0
                    for f in xs:
                        for c in ET.parse(os.path.join(cov_dir, f)).getroot().findall('counter'):
                            if c.get('type') == 'INSTRUCTION':
                                cv += int(c.get('covered')); tt += int(c.get('covered')) + int(c.get('missed'))
                    r['cov'] = 100 * cv / tt; r['source'] = 'raw'
                m = json.load(open(mp, encoding='utf-8')) if os.path.isfile(mp) else []
                if len(m) == r['total_mutants']:      # recount only when every mutant of the catalogue is listed
                    r['killed'] = sum(1 for x in m if x.get('killed'))
                    r['mut'] = 100 * r['killed'] / r['total_mutants']
            runs.append(r)
    return runs


def sd(xs): return statistics.stdev(xs) if len(xs) > 1 else float('nan')


def cell(runs, exp, app, cfg):
    def key(r):
        if r['experiment'] == 'validation': return r['prompt_version']
        if r['experiment'] == 'unpatched': return 'raw'
        return r['temperature']
    sel = [r for r in runs if r['experiment'] == exp and r['application'] == app and key(r) == cfg]
    return [r for r in sel if r['present']], len(sel)


def stats_of(present, app):
    n = len(present)
    if not n: return {'n': 0}
    pr, cv, mu = [r['pass_rate'] for r in present], [r['cov'] for r in present], [r['mut'] for r in present]
    kb, tot = KILLABLE[app]; bound = 100 * kb / tot
    out = dict(n=n, pass_mean=statistics.mean(pr), pass_min=min(pr), pass_max=max(pr),
               cov_mean=statistics.mean(cv), cov_sd=sd(cv), cov_se=sd(cv) / math.sqrt(n),
               mut_mean=statistics.mean(mu), mut_sd=sd(mu), mut_se=sd(mu) / math.sqrt(n),
               mut_min=min(mu), mut_max=max(mu),
               norm_mean=100 * statistics.mean(mu) / bound, norm_sd=100 * sd(mu) / bound,
               runs_at_upper_bound=sum(1 for r in present if r['killed'] >= kb))
    for s in present[0]['svc']:
        if all(s in r['svc'] for r in present):      # some spreadsheet rows record only the total coverage
            out['cov_mean:' + s] = statistics.mean(r['svc'][s] for r in present)
    return out


def compute(runs, a):
    exp, app, cfg, stat = a['experiment'], a['application'], a['config'], a['statistic']
    if stat == 'total_instructions':
        # Table 3.1 describes the applications of the main experiments (patched specifications);
        # the unpatched runs are listed separately because their build can differ.
        v = {r['total_instr'] for r in runs if r['present'] and r['application'] == app
             and r['experiment'] != 'unpatched'}
        u = sorted({r['total_instr'] for r in runs if r['present'] and r['application'] == app
                    and r['experiment'] == 'unpatched'})
        return (v.pop() if len(v) == 1 else float('nan')), 'patched runs (unpatched runs: %s)' % ', '.join(map(str, u))
    if stat == 'total_mutants':
        v = {r['total_mutants'] for r in runs if r['present'] and r['application'] == app}
        return (v.pop() if len(v) == 1 else float('nan')), 'all runs'
    if cfg != 'all':
        present, total = cell(runs, exp, app, cfg)
        st = stats_of(present, app)
        return st.get(stat, float('nan')), 'n=%d/%d' % (len(present), total)
    # statistics over several configurations
    configs = sorted({(r['experiment'], r['application'],
                       r['prompt_version'] if r['experiment'] == 'validation' else r['temperature'])
                      for r in runs if r['experiment'] == exp and (app == 'any' or r['application'] == app)})
    cells = []
    for e, ap, c in configs:
        present, total = cell(runs, e, ap, c)
        if present: cells.append((ap, stats_of(present, ap), len(present), total))
    note = '%d configurations' % len(cells)
    if stat.endswith('_se_typical'):
        m = stat.split('_')[0]
        return statistics.mean(st[m + '_se'] for _, st, _, _ in cells), note + ' (mean of sd/sqrt(n))'
    if stat in ('cov_spread', 'mut_spread'):
        m = stat.split('_')[0] + '_mean'
        return max(st[m] for _, st, _, _ in cells) - min(st[m] for _, st, _, _ in cells), note
    if stat in ('cov_spread_max', 'mut_spread_max'):
        m = stat.split('_')[0] + '_mean'; best = []
        for ap in sorted({c[0] for c in cells}):
            vals = [st[m] for a2, st, _, _ in cells if a2 == ap]
            best.append(max(vals) - min(vals))
        return max(best), note
    if stat == 'cov_se_max': return max(st['cov_se'] for _, st, _, _ in cells), note
    if stat == 'mut_se_min': return min(st['mut_se'] for _, st, _, _ in cells), note
    if stat == 'mut_se_max': return max(st['mut_se'] for _, st, _, _ in cells), note
    return float('nan'), 'unknown statistic'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--from-files', action='store_true', help='per-run values from the summary.json of each run')
    g.add_argument('--from-raw', action='store_true', help='recompute per-run values from XML and mutants.json')
    ap.add_argument('--csv', help='also write the comparison to this CSV file')
    args = ap.parse_args()
    source = 'raw' if args.from_raw else 'files' if args.from_files else 'manifest'
    runs = load_runs(source)
    rows, same = [], 0
    with open(os.path.join(SCRIPTS, 'thesis_aggregates.csv'), encoding='utf-8') as fh:
        aggs = list(csv.DictReader(fh))
    for a in aggs:
        value, note = compute(runs, a)
        d = int(a['decimals']); reported = float(a['value'])
        at_most = a.get('claim') == 'at most'
        if at_most:
            # the text states an upper bound ("at most X"): the recomputed value must not exceed it
            ok = not math.isnan(value) and value <= reported + 0.5 * 10 ** -d + 1e-9
            verdict = ('within (at most %s)' % a['value']) if ok else 'differs'
        else:
            # same value at the printed precision: the reported number is a rounding of the recomputed one
            ok = not math.isnan(value) and abs(value - reported) <= 0.5 * 10 ** -d + 1e-9
            verdict = 'same' if ok else 'differs'
        same += ok
        rows.append([a['where'], a['experiment'], a['application'], a['config'], a['statistic'], a['value'],
                     'n/a' if math.isnan(value) else '%.*f' % (d, value), verdict, note])
    w = [max(len(str(r[i])) for r in rows + [['where', 'experiment', 'application', 'config', 'statistic',
                                                'reported', 'recomputed', '', 'runs']]) for i in range(9)]
    head = ['where', 'experiment', 'application', 'config', 'statistic', 'reported', 'recomputed', '', 'runs']
    print('  '.join(h.ljust(w[i]) for i, h in enumerate(head)))
    last = None
    for r in rows:
        if r[0] != last and last is not None: print()
        last = r[0]
        print('  '.join(str(x).ljust(w[i]) for i, x in enumerate(r)))
    print('\n%d reported aggregates, %d recomputed with the same value at the printed precision (or within the '
          'stated bound), %d different.' % (len(rows), same, len(rows) - same))
    art = [r for r in rows if r[0].startswith('Article')]
    print('Article: %d of %d reproduced.' % (sum(1 for r in art if r[7] != 'differs'), len(art)))
    print('Per-run values taken from: %s' % {'manifest': 'manifest.csv', 'files': 'summary.json of each run',
                                             'raw': 'JaCoCo XML + mutants.json (summary.json where absent)'}[source])
    if args.csv:
        with open(args.csv, 'w', newline='', encoding='utf-8') as fh:
            cw = csv.writer(fh); cw.writerow(head); cw.writerows(rows)


if __name__ == '__main__':
    sys.exit(main())
