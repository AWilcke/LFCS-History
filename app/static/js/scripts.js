//DataTables ini
$(document).ready(function() {
  $('#results').dataTable({
      paging: false,
      "dom":'f',
      "oLanguage":{
        "sSearch":"Filter: "
      }
  });

});


//dynamic form function
$(function()
{
    $(document)
    .on('click', '.btn-add', function(e)
    {
        e.preventDefault();

        var controlForm = $('.controls .position-form'),
            currentEntry = $(this).parents('.entry'),
            newEntry = $(currentEntry.clone()).insertAfter(currentEntry);

        newEntry.find('input').val('');


        controlForm.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .html('<span class="glyphicon glyphicon-remove"></span>');
    })

    .on('click', '.btn-remove', function(e)
        {
                $(this).parents('.entry').remove();

                e.preventDefault();
                return false;
        });
});
