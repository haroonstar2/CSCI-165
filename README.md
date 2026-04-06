# League Jungle Path Finding Algorithm Visualization

**Class:** CSCI 165 Bio-Inspired Machine Learning  

## Description
This project visualizes various pathfinding and optimization algorithms to determine the most efficient route for a "Jungler" in League of Legends. The tool calculates the shortest path between a starting point, specific jungle camps (with logic for side-specific clears), and a final destination. It compares traditional search methods like **Dijkstra's** and **A*** with bio-inspired approaches like **Genetic Algorithms** and reinforcement learning via **Q-Learning** to navigate the complex map of Summoner's Rift.

## Demo
The tool provides a real-time visualization on a 64x64 grid mapped from the League of Legends minimap.

### Algorithm Visualizations
* **Dijkstra:** Traditional pathfinding algorithm to find the shortest path
* **A\* Search:** Efficiently finds the shortest path using a heuristic-based approach.
* **Genetic Algorithm:** Evolves a population of paths over multiple generations to find an optimal route.
* **Q-Learning:** Trains an agent through reinforcement to learn the optimal path by interacting with the environment.

* **Dijkstra's Demo:** ![Dijkstra Visualization](https://github.com/user-attachments/assets/6b59a5ea-1de3-40d9-93ca-4d668db96f1c)

* **A\* Demo:** ![A* Visualization](https://github.com/user-attachments/assets/64c36ac4-5af1-4ee5-aeb6-41f2beaf99ac)

* **GA Demo:** ![GA Visualization](https://github.com/user-attachments/assets/1519fa75-b945-46dd-827c-e7dccb7c020e)

* **Q-Learning Demo:** ![Q-Learning Visualization](https://github.com/user-attachments/assets/63ccfcab-7e3a-479b-af24-76abf7b3fc53)

## Instructions

### Prerequisites
* **Backend:** Python 3.10+
* **Frontend:** Node.js and npm

### Running the Backend
1. Navigate to the `backend` folder.
2.  Install dependencies: `pip install fastapi pydantic`
3.  Start the server: `fastapi dev`
    * The backend will run on `http://localhost:8000`.

### Running the Frontend
1.  Navigate to the `frontend` folder.
2.  Install dependencies: `npm install`
3.  Start the development server: `npm run dev`
4.  Open your browser to the URL provided by Vite (typically `http://localhost:5173`).

### Using the Tool
1.  **Select Side:** Choose "Blue" or "Red" side from the controls.
2.  **Set Points:** Click on the map to set a **Start (S)** and a **Target (T)** location.
3.  **Choose Algorithm:** Select an algorithm from the dropdown.
4.  **Simulate:** Press **Start** to watch the algorithm find the path. Use the **Speed Slider** to adjust the visualization speed.

## Tech Stack
* **Frontend:** React 19, Zustand (State Management), Material UI (Components), Vite.
* **Backend:** FastAPI (Python), Pydantic (Data Validation).
* **Algorithms:** 
    * Custom Dijkstra's
    * Custom A\* implementation with Euclidean heuristics.
    * Genetic Algorithm with tournament selection and crossover.
    * Q-Learning with ε-greedy policy.
