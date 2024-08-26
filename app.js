document.addEventListener("DOMContentLoaded", () => {
    const board = document.getElementById("board");
    const messageElement = document.getElementById("message");
    const moveControls = document.getElementById("move-controls");
    const newGameButton = document.getElementById("new-game");

    let selectedCharacter = null;
    let currentPlayer = "A"; // Player A starts the game
    let gameOver = false;
    const socket = new WebSocket("ws://localhost:8765");

    // Initialize the board
    function initializeBoard() {
        board.innerHTML = "";
        for (let i = 0; i < 5; i++) {
            for (let j = 0; j < 5; j++) {
                const cell = document.createElement("div");
                cell.classList.add("cell");
                cell.dataset.row = i;
                cell.dataset.col = j;
                board.appendChild(cell);
            }
        }
    }

    // Render the board with current game state
    function renderBoard(gameState) {
        const cells = document.querySelectorAll(".cell");
        cells.forEach(cell => {
            const row = cell.dataset.row;
            const col = cell.dataset.col;
            const character = gameState[row][col];
            if (character) {
                cell.textContent = character;
                cell.classList.add("occupied");
            } else {
                cell.textContent = "";
                cell.classList.remove("occupied");
            }
        });
    }

    // Handle character selection
    board.addEventListener("click", (event) => {
        if (gameOver) return;
        const cell = event.target.closest(".cell");
        if (!cell || !cell.classList.contains("occupied")) return;

        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const character = cell.textContent;

        if (character.startsWith(currentPlayer)) {
            selectedCharacter = { row, col, character };
            displayValidMoves(character);
        }
    });

    // Display valid moves for the selected character
    function displayValidMoves(character) {
        moveControls.innerHTML = "";
        const characterType = character.split("-")[1];
        let moves = [];
        switch (characterType) {
            case "P1":
            case "P2":
            case "P3":
                moves = ["L", "R", "F", "B"];
                break;
            case "H1":
                moves = ["L", "R", "F", "B"];
                break;
            case "H2":
                moves = ["FL", "FR", "BL", "BR"];
                break;
        }

        moves.forEach(move => {
            const button = document.createElement("button");
            button.textContent = move;
            button.addEventListener("click", () => handleMove(character, move));
            moveControls.appendChild(button);
        });
    }

    // Handle move selection
    function handleMove(character, move) {
        if (!selectedCharacter) return;
        const moveCommand = `${selectedCharacter.character}:${move}`;
        socket.send(JSON.stringify({ type: "move", move: moveCommand }));
    }

    // Handle websocket messages from the server
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        switch (data.type) {
            case "gameState":
                renderBoard(data.gameState);
                currentPlayer = data.currentPlayer;
                messageElement.textContent = `Player ${currentPlayer}'s turn`;
                break;
            case "invalidMove":
                alert("Invalid move! Please try again.");
                break;
            case "gameOver":
                gameOver = true;
                messageElement.textContent = `Game over! Player ${data.winner} wins!`;
                break;
            case "newGame":
                gameOver = false;
                currentPlayer = "A";
                initializeBoard();
                renderBoard(data.gameState);
                messageElement.textContent = `Player A's turn`;
                break;
        }
    };

    // Handle new game button click
    newGameButton.addEventListener("click", () => {
        socket.send(JSON.stringify({ type: "newGame" }));
    });

    // Initialize the board on page load
    initializeBoard();
});
