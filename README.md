# WeaveSuite

WeaveSuite generates suites of **system tests for microservice applications running on Kubernetes** with a Large Language Model, keeping a human in the loop:
1. **Discover:** once deployed in the cluster, it finds the live microservices and retrieves their OpenAPI specifications.
2. **Verify the specifications:** an operator checks that every microservice was discovered and that each specification is complete enough to write black-box tests from.
3. **Generate:** the verified specifications are given to the LLM (Google Gemini 3.1 Pro), which writes a pytest suite of system tests.
4. **Review and run:** an operator reviews the suite, then WeaveSuite runs it against the live services and reports the results and the endpoint coverage.

## Repository layout

| Folder | Content |
|---|---|
| [`WeaveSuiteBackend/`](WeaveSuiteBackend) | FastAPI backend (thesis Sec. 4.1.1). It has five services in `src/services/`: discovery, specifications, generation, test execution and endpoint coverage. The final prompt (v30, thesis Listing A.9) is in `src/services/generation_service.py`. The human-verified patches of the OpenAPI specifications (thesis Sec. 3.3, Appendix A.1) are in `src/patches/`. |
| [`WeaveSuiteUI/`](WeaveSuiteUI) | Next.js web interface (thesis Sec. 4.1.3) for reviewing specifications and tests and viewing coverage. |
| [`mutants/`](mutants) | The 96 mutants used for mutation testing (37 SockShop, 27 KubePay, 32 Lakeside Mutual), one patch each, with their catalogue. |
| [`results/`](results) | The raw data of every run reported in the article and the thesis, with a script that recomputes every reported number. |

## Reproducing the reported numbers

```bash
python results/scripts/recompute_aggregates.py
```

Python 3 standard library only, no cluster needed. The script recomputes every mean, standard deviation, spread and normalized score reported in the article (Fig. 2, Sec. IV) and in the thesis from the per-run data in [`results/`](results), and prints each one next to the reported value. [`results/README.md`](results/README.md) maps every table and figure to its folders and explains the content of a run.

## Applications under test

| Application | Role | Source |
|---|---|---|
| SockShop | validation (prompt engineering) | [helidon-sockshop/sockshop](https://github.com/helidon-sockshop/sockshop) |
| KubePay | validation (prompt engineering) | [teamlead/spring-microservices-kubernetes-demo](https://github.com/teamlead/spring-microservices-kubernetes-demo) |
| Lakeside Mutual | held-out evaluation | [Microservice-API-Patterns/LakesideMutual](https://github.com/Microservice-API-Patterns/LakesideMutual) |

## Running WeaveSuite

WeaveSuite runs inside the Kubernetes cluster of the application under test (thesis Sec. 4.1). It has three parts:
- **Backend:** one container (`WeaveSuiteBackend/Dockerfile`, port 8000). It discovers services through the in-cluster Kubernetes API, so its service account needs permission to list services in the cluster.
- **Database:** PostgreSQL, used by the backend.
- **Web UI:** one container (`WeaveSuiteUI/Dockerfile`, port 3000) that reaches the backend at `API_BASE_URL` (default `http://weavesuite-backend:8000`).

```bash
docker build -t weavesuite-backend WeaveSuiteBackend
docker build -t weavesuite-ui WeaveSuiteUI
```

Backend configuration (environment variables):

| Variable | Use |
|---|---|
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB` | Database connection |
| `GOOGLE_API_KEY` | Gemini API key used for test generation (model `gemini-3.1-pro-preview`) |

Main backend endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /api/specs`, `POST /api/update-specs` | Discovered specifications |
| `POST /api/generate-tests` | Generate the suite |
| `GET /api/system-tests` | Read the suite |
| `POST /api/execute-tests`, `POST /api/execute-test/{id}` | Run the suite, or one test |
| `/api/coverage/...` | Endpoint coverage |

## License

[MIT](LICENSE).
