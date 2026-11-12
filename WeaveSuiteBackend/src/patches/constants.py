#sentinel for key deletion in spec patches
DELETE = type("DELETE", (), {"__repr__": lambda self: "DELETE"})()