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


//dynamic form functions

//on first load, replace all non-needed + with -
$(document).ready(function(){
    $('.dynamic-form').find('.entry:not(:last) .btn-add')
        .removeClass('btn-add').addClass('btn-remove')
        .html('<i class="glyphicon glyphicon-remove"></i>');
});

//function for adding/removing forms
$(function()
{
    $(document)
    .on('click', '.btn-add', function(e)
    {
        e.preventDefault();

        var controlForm = $('.dynamic-form'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).insertAfter(currentEntry);
        
        //clear value
        newEntry.find('input').val('');
        
        //change name of date form, to link up with relevant position
        var oldName = newEntry.find('.date-entry input').attr('name');

        if(oldName){
            var newNum = (parseInt(oldName.split('_')[1], 10) + 1).toString(),
                type = oldName.split('_')[0];

            newEntry.find('.date-entry .datestart').attr('name', type.concat('_').concat(newNum.concat('_start')));
            newEntry.find('.date-entry .dateend').attr('name', type.concat('_').concat(newNum.concat('_end')));
        }

        //so that the cloning only picks up one date-entry
        if(newEntry.find('.date-entry').length>1){
            toDelete = newEntry.find('.date-entry:not(:first)').remove();
            newEntry.find('.date-entry .date-remove')
                .removeClass('date-remove').addClass('date-add')
                .html('<i class="glyphicon glyphicon-plus"></i>');
        }

        controlForm.find('.entry:not(:last) .btn-add')
            .removeClass('btn-add').addClass('btn-remove')
            .html('<i class="glyphicon glyphicon-remove"></i>');
    })

    .on('click', '.btn-remove', function(e)
        {
                $(this).parents('.entry:first').remove();
                
                //update date indexes
                var dateForm = $('.position-date-form');
                
                for(i=0;i<dateForm.length;i++){
                    var type = dateForm.eq(i).find('.form-control').eq(0).attr('name').split('_')[0];
                    dateForm.eq(i).find('.datestart').attr('name',type.concat('_').concat(i.toString().concat('_start')));
                    dateForm.eq(i).find('.dateend').attr('name',type.concat('_').concat(i.toString().concat('_end')));
                }

                e.preventDefault();
                return false;
        });
});

//first load
$(document).ready(function(){
    $('.position-date-form').find('.date-entry:not(:last) .btn-add')
        .removeClass('btn-add').addClass('btn-remove')
        .html('<i class="glyphicon glyphicon-remove"></i>');
});

//for nested date forms
$(function()
{
    $(document)
    .on('click', '.date-add', function(e)
    {
        e.preventDefault();

        var form = $(this).parents('.position-date-form:first'),
            current = form.find('.date-entry:first'),
            newEntry = $(current.clone()).insertAfter(current);
            
        newEntry.find('input').val('');

        //insert blank to preserve formatting        
        var elem=document.createElement('div');
        elem.id='blank';
        elem.className='col-xs-6';
        $(newEntry).prepend(elem);

        form.find('.date-entry:not(:last) .date-add')
            .removeClass('date-add').addClass('date-remove')
            .html('<i class="glyphicon glyphicon-remove"></i>');
    })

    .on('click', '.date-remove', function(e)
        {
            $(this).parents('.date-entry:first').remove();
            e.preventDefault();
            return false;
        });
});
