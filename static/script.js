var board = null;
var game = new Chess();
var $status = $('#status');
var $advice = $('#advice');

// Dark mode functionality
function setTheme(isDark) {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(!isDark);
}

// Initialize theme from localStorage or system preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    setTheme(savedTheme === 'dark');
} else {
    setTheme(window.matchMedia('(prefers-color-scheme: dark)').matches);
}

function onDragStart(source, piece, position, orientation) {
    if (game.game_over()) return false;
    if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
        (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
        return false;
    }
}

function onDrop(source, target) {
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q'
    });

    if (move === null) return 'snapback';
    clearHighlights(); // Clear highlights after a move is made
    updateStatus();
}

function updateStatus() {
    var status = '';
    var moveColor = game.turn() === 'b' ? 'Black' : 'White';
    
    if (game.in_checkmate()) {
        status = 'Game over, ' + moveColor + ' is in checkmate.';
    } else if (game.in_draw()) {
        status = 'Game over, drawn position';
    } else {
        if (game.in_check()) {
            status = '<span class="turn check">' + moveColor + '</span> to move (in check)';
        } else {
            status = '<span class="turn">' + moveColor + '</span> to move';
        }
    }

    $status.html('<h2>' + status + '</h2>');
    // Clear advice when status changes
    $advice.html('Click "Get AI Advice" for move suggestions');
}

function getStockfishAdvice() {
    $advice.html('Analyzing position...');
    
    fetch('/get_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fen: game.fen()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.move) {
            const source = data.move.slice(0, 2);
            const target = data.move.slice(2, 4);
            highlightBestMove(source, target);
            $advice.html('Best move: ' + source + ' to ' + target + '<br>Evaluation: ' + data.eval);
        }
    })
    .catch(error => {
        console.error('Error getting advice:', error);
        $advice.html('Error getting advice: ' + error);
    });
}

function clearHighlights() {
    $('.square-55d63').removeClass('highlight');
}

function highlightBestMove(source, target) {
    clearHighlights();
    $('.square-' + source).addClass('highlight');
    $('.square-' + target).addClass('highlight');
}

var config = {
    position: 'start',
    draggable: true,
    pieceTheme: 'https://lichess1.org/assets/piece/cburnett/{piece}.svg',
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: function() {
        board.position(game.fen());
    }
};

$(document).ready(function() {
    board = Chessboard('board', config);
    updateStatus();
    
    $('#resetBtn').on('click', function() {
        game.reset();
        board.start();
        clearHighlights();
        updateStatus();
    });
    
    $('#getAdviceBtn').on('click', getStockfishAdvice);
    $('#darkModeToggle').on('click', toggleTheme);

    // Ensure pieces are loaded
    setTimeout(function() {
        if (!board.position()) {
            board.start();
        }
    }, 100);
});
