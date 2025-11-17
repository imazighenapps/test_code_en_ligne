
$(document).ready(function() {
  
    var $focus =0;

    $("tr>td.distance").focusout(function() {
        $focus++
        console.log(this);
        console.log($focus);
        $(this).closest('td').next('td').find('.distance').focus();
        // distance
    })
   
   
});