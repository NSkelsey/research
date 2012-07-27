
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

// for filter_selector
function hide_trs(sel){
  var choice = sel.val();
  sel.closest("tbody").children().each(function(){
    if ($(this).find("." + choice).length){
      $(this).css("display", "table-row");
    } 
    else if ($(this).find(".filter_selector").length){
      $(this).css("display", "table-row");
    }
    else if ($(this).find(".notfilter").length){
      $(this).css("display", "table-row");
    }
    else if ($(this).find(".filter_choice").length){
      $(this).css("display", "table-row");
    }
    else {
      $(this).css("display", "none");
    }
  });
}

function hide_on_filter_choice(sel){
  var val = sel.val();
  if (val != "new_form"){
    sel.closest("tbody").children().each(function(){
      if ($(this).find(".notfilter").length)
        {
          $(this).css("display", "table-row");
        } 
        else if ($(this).find(".filter_choice").length)
        {
          $(this).css("display", "table-row");
        }
        else
          {
          $(this).css("display", "none");
          }
    });
  } else {
    var choice = sel.closest("tbody").find("select.filter_selector")
    hide_trs(choice);
  }
}

$(document).ready(function() {
  $("select.filter_selector").each(function() {
    hide_trs($(this));
  });
  $("select.filter_choice").each(function() {
    hide_on_filter_choice($(this));
  });
  $("a.duplicate").click(function() {
    var div = $(this).closest("div")
    cloneMore(div, "form"); 
  });
  $("a.delete").click(function() {
    var div = $(this).closest("div");
    delete_div(div, "form");
  });

  $("select.filter_selector").change(function() {
    hide_trs($(this));
  });

  $("select.filter_choice").change(function() {
    var sel = $(this);
    hide_on_filter_choice(sel);
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


function display() {

  var class_ = $(this).attr("value");
  var tbody = $(this).closest("table");
  tbody.find("tr:not(." + class_ + ")").css("display","none");
  tbody.find("." + class_ + "").css("display", "table-row");
  $(this).closest("tr").css("display", "table-row");
  tbody.find(".notfilter").css("display","table-row");
  tbody.find("#id_logical_operation").closest("tr").css("display","table-row");

};





