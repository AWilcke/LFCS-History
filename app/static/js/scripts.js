//Select2
$(document).ready(function() {
      $("select").select2();
});


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
    $('.dynamic-form').find('.entry:not(:last) .btn-add').remove();
});

//function for adding/removing forms
//might write separate function for select2 things
$(function()
{
    $(document)
    .on('click', '.btn-add', function(e)
    {
        e.preventDefault();

        var controlForm = $(this).parents('.dynamic-form:first'),
            currentEntry = $(this).parents('.entry:first');
        
        //Select2 special case
        if(currentEntry.find('select').length!=0){
            currentEntry.find('select').select2('destroy');

            var newEntry = $(currentEntry.clone());
           //clear first
            newEntry.insertAfter(currentEntry);
            $('select').select2();
            newEntry.find('select').val('').change();
        }
        else{
            var newEntry = $(currentEntry.clone()).insertAfter(currentEntry);
        }
        
        //clear value
        //need to clear "value" of eg. dates
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
            newEntry.find('.date-entry:not(:last)').remove();
            newEntry.find('#dates').removeClass('col-xs-offset-4');
        }
        
        controlForm.find('.entry:not(:last) .btn-add').remove();
    })

    .on('click', '.btn-remove', function(e)
        {
            var form = $(this).parents('.dynamic-form:first'),
                current = $(this).parents('.entry:first'),
                first = form.find('.entry:first'),
                last = form.find('.entry:last'),
                button = $(current.find('.btn-add')).clone();
            
            if(first.is(last)){
                current.find('input').val('');
                
                //select2 clearing
                current.find('select').val('').change();

                e.preventDefault();
                return false;
            }

            $(this).parents('.entry:first').remove();
            form.find('.entry:last div:last').append(button);
            
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
    //preserve formatting
    $('.position-date-form').find('.date-entry:not(:first) #dates').addClass('col-xs-offset-4');
    //get relevant buttons
    $('.position-date-form').find('.date-entry:not(:last) .date-add').remove();
});

//for nested date forms
$(function()
{
    $(document)
    .on('click', '.date-add', function(e)
    {
        e.preventDefault();
        //clone first entry
        var form = $(this).parents('.position-date-form:first'),
            current = $(this).parents('.date-entry:first'),
            newEntry = $(current.clone()).insertAfter(current);

        newEntry.find('input').val('');

        //insert blank to preserve formatting
        newEntry.find('#dates').attr('class','col-xs-6 col-xs-offset-4');
        //get relevant buttons
        form.find('.date-entry:not(:last) .date-add').remove();

    })

    .on('click', '.date-remove', function(e)
        {   
            var form = $(this).parents('.position-date-form:first'),
                current = $(this).parents('.date-entry:first'),
                first = form.find('.date-entry:first'),
                last = form.find('.date-entry:last'),
                button = $(current.find('.date-add')).clone();

            if(first.is(last)){
                current.find('input').val('');
                e.preventDefault();
                return false;
            }
            else if(current.is(first)){
                current.next().find('#dates').removeClass('col-xs-offset-4');
            }

            $(this).parents('.date-entry:first').remove();
            form.find('.date-entry:last div:last').append(button);

            e.preventDefault();
            return false;
        });
});
