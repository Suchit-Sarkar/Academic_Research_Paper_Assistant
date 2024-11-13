Running Sequence of the Project


1. Use the following command to install the dependencies.
	pip install -r requirements.txt

2. Start the Neo4j Database:

Ensure Neo4j is running on your local machine or specified server (default URI: neo4j://localhost:7687).
Check that the credentials match your Neo4j setup (neo4j_user and neo4j_password).
Run FastAPI Server:

3. Start the FastAPI server (FastAPI_Server.py).
Use a command such as:

uvicorn FastAPI_Server:app --reload
This will initialize the FastAPI server on the default port (8000) unless otherwise specified. 
The server will handle requests from the Streamlit frontend and communicate with the Neo4j database.
Launch Streamlit Frontend:

4. Run the streamlit_frontend.py file to start the Streamlit interface:
streamlit run streamlit_frontend.py

This will open the Streamlit frontend in a web browser, which interacts with the FastAPI server.