function toggleHiragana(button) {
    const hiraganaSpan = button.previousElementSibling; // Get the span before the button
    hiraganaSpan.classList.toggle('hidden');
    }

function toggleMeaning(button) {
    const meaningSpan = button.previousElementSibling;
    meaningSpan.classList.toggle('hidden');
    }