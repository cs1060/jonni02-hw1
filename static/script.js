var board = null;
var game = new Chess();
var $status = $('#status');
var $advice = $('#advice');

// Theme handling
function initTheme() {
    // Set dark mode as default if no theme is stored
    if (!localStorage.getItem('theme')) {
        localStorage.setItem('theme', 'dark');
        document.documentElement.setAttribute('data-theme', 'dark');
    } else {
        const theme = localStorage.getItem('theme');
        document.documentElement.setAttribute('data-theme', theme);
    }
}

function setTheme(isDark) {
    document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
}

function toggleTheme() {
    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    setTheme(!isDark);
}

// Initialize theme on page load
initTheme();

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
        status = 'Game over, <span class="turn">' + moveColor + '</span> is in checkmate.';
    } else if (game.in_draw()) {
        status = 'Game over, <span class="turn">drawn position</span>';
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
    const $loadingDots = $('<span>').addClass('loading-dots').text('...');
    $advice.html('Analyzing position').append($loadingDots);
    
    // Add timeout to the fetch
    const timeoutDuration = 5000; // 5 seconds
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutDuration);
    
    fetch('/get_move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            fen: game.fen()
        }),
        signal: controller.signal
    })
    .then(response => {
        clearTimeout(timeoutId);
        if (!response.ok) {
            return response.json().then(err => {
                throw new Error(err.error || 'Failed to get move suggestion');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.move) {
            const source = data.move.slice(0, 2);
            const target = data.move.slice(2, 4);
            highlightBestMove(source, target);
            
            let scoreText = '';
            if (typeof data.score === 'number') {
                const absScore = Math.abs(data.score / 100); // Convert centipawns to pawns
                scoreText = data.score > 0 ? `+${absScore.toFixed(1)}` : `-${absScore.toFixed(1)}`;
            }
            
            $advice.html(`
                <div>Best move: <strong>${source} → ${target}</strong></div>
                ${scoreText ? `<div>Evaluation: <strong>${scoreText}</strong></div>` : ''}
            `);
        } else {
            $advice.html('No analysis available for this position');
        }
    })
    .catch(error => {
        console.error('Error getting advice:', error);
        if (error.name === 'AbortError') {
            $advice.html('Request timed out. Please try again.');
        } else {
            $advice.html(error.message || 'Error getting move suggestion. Please try again.');
        }
        clearHighlights();
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
