// custom javascript
$(document).ready(function() {
    $.ajax({
        url: '{{ url_for("vendor.search") }}'
    }).done(function (data) {
        $('input').autocomplete({
            source: data,
            minLength: 2
        });
    });
}

