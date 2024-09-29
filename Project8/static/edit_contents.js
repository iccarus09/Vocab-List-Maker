$(document).ready(function() {
    // Handle form submission
    $('#add-contents-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '/edit-contents',
            method: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                // Add new row to the table
                var newRow = '<tr data-id="' + response.ID + '">' +
                    '<td><a href="' + response.Link + '" target="_blank">' + response.Title + '</a></td>' +
                    '<td>' + response.Level + '</td>' +
                    '<td>' + response.Vocab_Count + '</td>' +
                    '<td><button class="btn-delete" data-id="' + response.ID + '">Delete</button></td>' +
                    '</tr>';
                $('#contents-table tbody').append(newRow);
                // Clear the form
                $('#add-contents-form')[0].reset();
            }
        });
    });

    // Handle delete button clicks
    $(document).on('click', '.btn-delete', function() {
        var contentId = $(this).data('id');
        $.ajax({
            url: '/edit-contents',
            method: 'DELETE',
            data: { id: contentId },
            success: function(response) {
                if (response.status === 'success') {
                    $('tr[data-id="' + contentId + '"]').remove();
                }
            }
        });
    });
});