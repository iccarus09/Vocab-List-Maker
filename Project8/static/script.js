function toggleHiragana(button) {
    const hiraganaSpan = button.previousElementSibling; // Get the span before the button
    hiraganaSpan.classList.toggle('hidden');
    }

function toggleMeaning(button) {
    const meaningSpan = button.previousElementSibling;
    meaningSpan.classList.toggle('hidden');
    }

// Filter view
document.addEventListener('DOMContentLoaded', function() {
    const table = document.getElementById('vocab-table');
    if (!table) return; // Exit if we're not on the vocab page

    const rows = table.getElementsByTagName('tr');

    function filterTable(showMemorized) {
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const checkbox = row.querySelector('input[type="checkbox"]');
            const isMemorized = checkbox.checked;
            if (showMemorized === 'all' || (showMemorized && isMemorized) || (!showMemorized && !isMemorized)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    }

    document.getElementById('show-memorized')?.addEventListener('click', function() {
        filterTable(true);
    });

    document.getElementById('show-unmemorized')?.addEventListener('click', function() {
        filterTable(false);
    });

    document.getElementById('show-all')?.addEventListener('click', function() {
        filterTable('all');
    });
});