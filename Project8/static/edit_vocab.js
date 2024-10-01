console.log("edit_vocab.js has been loaded");

$(document).ready(function() {
    console.log("Document ready, jQuery loaded");
    // Handle form submission
    $('#add-vocab-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '/edit-vocab/' + {{ title_id }},
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                // Add new row to the table
                var newRow = '<tr data-id="' + response.ID + '">' +
                    '<td>' + response.Kanji + '</td>' +
                    '<td>' + response.Hiragana + '</td>' +
                    '<td>' + response.Meaning + '</td>' +
                    '<td><button class="btn-delete" data-id="' + response.ID + '">Delete</button></td>' +
                    '</tr>';
                $('#vocab-table tbody').append(newRow);
                // Clear the form
                $('#add-vocab-form')[0].reset();
            },
        });
    });

//    // Handle delete button clicks
//    $(document).on('click', '.btn-delete', function() {
//        console.log("Delete button clicked");
//        var itemId = $(this).data('id');
//        console.log("Item ID:", itemId);
//
//        $.ajax({
//            url: '/edit-vocab/' + title_id,
//            method: 'DELETE',
//            data: { id: itemId },
//            success: function(response) {
//                console.log("AJAX success:", response);
//                if (response.status === 'success') {
//                    $('tr[data-id="' + itemId + '"]').remove(); // Remove row from table
//                    console.log("Row removed from table");
//                }
//            },
//            error: function(xhr, status, error) {
//                console.error("AJAX error:", status, error);
//                console.log("Response text:", xhr.responseText);
//            }
//        });
//    });
});

//document.getElementById('btn-delete').addEventListener('click', function(event) {
//console.log('Delete button clicked');
//// Add any relevant data you want to check
//console.log('Data to delete:', dataToDelete);
//// Proceed with delete logic...
//});