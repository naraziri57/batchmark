# batchmark

> CLI tool to benchmark batch jobs and output structured timing reports

---

## Installation

```bash
pip install batchmark
```

Or install from source:

```bash
git clone https://github.com/yourname/batchmark.git && cd batchmark && pip install .
```

---

## Usage

Run a benchmark against any shell command or script:

```bash
batchmark run "python process_data.py --input data.csv" --iterations 10
```

Output a structured JSON timing report:

```bash
batchmark run "my_batch_job.sh" --iterations 5 --output report.json
```

Example report output:

```json
{
  "command": "my_batch_job.sh",
  "iterations": 5,
  "mean_seconds": 3.42,
  "min_seconds": 3.10,
  "max_seconds": 3.89,
  "std_dev": 0.28
}
```

Available options:

| Flag | Description |
|------|-------------|
| `--iterations` | Number of times to run the job (default: 3) |
| `--output` | Path to write the JSON report |
| `--format` | Output format: `json`, `csv`, or `table` (default: `table`) |
| `--warmup` | Number of warmup runs before timing begins |

---

## License

This project is licensed under the [MIT License](LICENSE).