# Impersonal data

## Add new files
To add new files:

- Add the files to the Data folder.

Execute these lines:
```bash
cd APP-cli
python texty_gen_cli.py --data_file mydata.jsonl --Categories_file config.json
python data_for_frontend.py
```

Adjust the value of `mydata.jsonl`. The configuration file should remain static.

This will generate all required files and copy them to the frontend folder.

## Deploy the frontend

To deploy the frontend in development mode:

```bash
cd impersonal-frontend
npm run dev
```

To build the frontend for server deployment:

```bash
cd impersonal-frontend
npm run build-only
```

