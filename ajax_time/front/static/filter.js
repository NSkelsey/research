
function cloneMore(selector, type) {
  var newElement = $(selector).clone(true);
  var total = $('#id_' + type + '-TOTAL_FORMS').val();
  total++;
  $('#id_' + type + '-TOTAL_FORMS').val(total);
  $(selector).after(newElement);
  reorder(total);
}

function reorder(total){
  $("div.mytable").each(function (i) {
    $(this).find(':input').each(function() {
      var name = $(this).attr('name').replace(/-\d*-/,'-' + i + '-');
      var id = 'id_' + name;
      $(this).attr({'name': name, 'id': id});
    });
    $(this).find('label').each(function() {
      var newFor = $(this).attr('for').replace(/-\d*-/,'-' + i + '-');
      $(this).attr('for', newFor);
    });



  });
}

function delete_div(selector, type){
  $(selector).remove()
  var total = $('#id_' + type + '-TOTAL_FORMS').val();
  total--;
  $('#id_' + type + '-TOTAL_FORMS').val(total);
  reorder(total);

}


$(document).ready(function() {
  //$("tr #id_filter_selector").change(display)
  $("p.duplicate").click(function() {
    var div = $(this).closest("div")
    cloneMore(div, "form"); 
  });
  $("p.delete").click(function() {
    var div = $(this).closest("div");
    delete_div(div, "form");
  });
});



var t_count = 0;
function duplicate_table() {
  $("tbody").each(function(i, domEle){
    $(this).closest("table").find("tr #id_logical_operation").attr("onchange", "");
  });
  var and = $("#id_filter_selector").closest("table").clone()
  and.find("tr #id_logical_operation").attr("onchange", "duplicate_table()");
  and.attr("id", "clone").appendTo($("#out_form"));
  //and.find("tr #id_filter_selector").change(display);
};



