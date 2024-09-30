function toggleHiragana(button) {
    const hiraganaSpan = button.previousElementSibling; // Get the span before the button
    hiraganaSpan.classList.toggle('hidden');
    }

function toggleMeaning(button) {
    const meaningSpan = button.previousElementSibling;
    meaningSpan.classList.toggle('hidden');
    }

function submitForm() {
    // Clear inputs
    document.getElementById("add-vocabulary-form").reset(); // Resets all fields
    return true; // Allow form submission to proceed "return submitForm"
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

// Duplicate error pop up
document.getElementById('add-vocabulary-form').addEventListener('submit', function(event) {event.preventDefault();

    const formData = new FormData(this);

    // Extract title_id from the URL
    const pathSegments = window.location.pathname.split('/');
    const titleId = pathSegments[pathSegments.length - 1]; // Get the last segment of the path

    fetch(`/vocab/${titleId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showPopup(data.error); // Show error message in popup
        } else {
            alert(data.success); // Or another way to notify success
        }
    })
    .catch(error => console.error('Error:', error));
});

function showPopup(message) {
    document.getElementById('popupMessage').innerText = message;
    document.getElementById('popup').style.display = 'flex'; // Show the popup
}

function closePopup() {
    document.getElementById('popup').style.display = 'none'; // Hide the popup
}