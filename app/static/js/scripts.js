$(document).ready(function() {
  $('#results').dataTable({
      paging: false,
      "dom":'f',
      "oLanguage":{
        "sSearch":"Filter: "
      }
  });

});
