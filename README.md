# LangChain Examples

### Project setup
Run `chmod +x setup.sh`


### Sample queries
- What is the current status of our inventory?
- What are the year-over-year sales trends?
- Who are our top customers by sales volume?
- How much did our top customer order over the last six months?


### Installation.
- Copy `.env.example` to `.env` and update `OPENAI_API_KEY`.
- Run `chmod -x setup.sh`   <<< This will create a virtual env in project's root dir and activate it will all of the required dependencies.
- Vue app: `cd frontend && yarn install`


### Running project
1. CLI mode: run `python cli.py`  <<< This will start asking question on terminal.
2. API + Vue app: 
   - run `python api.py`  <<< Start fast api server at localhost:4000
   - run `yarn serve`     <<< Start frontend at localhost:8080

To quit from terminal while asking the question just type `exit` or `quit`

### Demo
[![Demo](https://raw.githubusercontent.com/aasimkhan/langchain-examples/main/docs/demo/thumbnail.jpg)](https://raw.githubusercontent.com/aasimkhan/langchain-examples/main/docs/demo/video.mp4
