//Update active
/*
$(document).ready(function() {
    $('.nav').find('.active').removeClass('active');
    var url = document.URL,
        viewAllre = /.*viewall.*//*;
    if (viewAllre.exec(url)) {
        $('.nav').find('#viewall').addClass('active');
    }
}); 
*/

//Select2
$(document).ready(function() {
      $(".select2").select2();
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
$(document).ready(function() {
  $('.datatable').dataTable({
      paging: false,
      "order":[[1, 'desc']],
      "dom":'rt',
  });

});

//prevent enter from submitting forms accidentally
$(document).ready(function() {
  $(window).keydown(function(event){
    var is_search = $(document).find("input[name='search']").length;
    if((event.keyCode == 13) && (is_search==0)) {
      event.preventDefault();
      return false;
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

        //also increment grant index
        var name = newEntry.find('.grant-entry select').attr('name');
        if(name){
            var oldNum = name.split('_')[1],
                newNum = parseInt(oldNum, 10) + 1;
            newEntry.find('.grant-entry select').attr('name', 'grant_'.concat(newNum).concat('_link'));
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
            form.find('.entry:last .cat-btn').append(button);
            
            //update date indexes
            var dateForm = $('.position-date-form');
            
            for(i=0;i<dateForm.length;i++){
                var type = dateForm.eq(i).find('.form-control').eq(0).attr('name').split('_')[0];
                dateForm.eq(i).find('.datestart').attr('name',type.concat('_').concat(i.toString().concat('_start')));
                dateForm.eq(i).find('.dateend').attr('name',type.concat('_').concat(i.toString().concat('_end')));
            }

            //update grant indexes
            var grantForm = $('.grant-secondary-form');
            
            for(i=0;i<grantForm.length;i++){
                grantForm.eq(i).find('.grant_link').attr('name','grant_'.concat(i.toString().concat('_link')));
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

//for grant secondary investigators
$(document).ready(function(){
    //get relevant buttons
    $('.grant-secondary-form').find('.grant-entry:not(:last) .grant-add').remove();
});

//for nested date forms
$(function()
{
    $(document)
    .on('click', '.grant-add', function(e)
    {
        e.preventDefault();
        //clone first entry
        var form = $(this).parents('.grant-secondary-form:first'),
            current = $(this).parents('.grant-entry:first');
        
        current.find('select').select2('destroy');

        var newEntry = $(current.clone());
        newEntry.insertAfter(current);
       
       //clear first
        $('select').select2();
        newEntry.find('select').val('').change();

        //get relevant buttons
        form.find('.grant-entry:not(:last) .grant-add').remove();

    })

    .on('click', '.grant-remove', function(e)
        {   
            var form = $(this).parents('.grant-secondary-form:first'),
                current = $(this).parents('.grant-entry:first'),
                first = form.find('.grant-entry:first'),
                last = form.find('.grant-entry:last'),
                button = $(current.find('.grant-add')).clone();

            if(first.is(last)){
                current.find('select').val('').change();
                e.preventDefault();
                return false;
            }

            $(this).parents('.grant-entry:first').remove();
            form.find('.grant-entry:last div:last').append(button);

            e.preventDefault();
            return false;
        });
});
//for password confirmation
$(function()
{
    $(document)
    .on('click', '.user-update', function(e)
        {
            var password = document.getElementById('password'),
                confirmation = document.getElementById('confirm_password');
            
            if (password.value != confirmation.value){
                if ($(confirmation).parents('div:first').find('.errormsg').length==0){
                    
                    var errorMessage = document.createElement('div'),
                        passForm = $(confirmation).parents('.form-group:first');
                    
                    $(errorMessage).attr('class','errormsg');
                    $(errorMessage).attr('style','color: red');
                    errorMessage.innerHTML = 'Passwords do not match'
                    $(errorMessage).insertAfter(confirmation);
                    
                    passForm.attr('class','form-group has-error');    
                }
                return false;
            }
            return true;
        });
});
