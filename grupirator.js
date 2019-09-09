let data_words = new Map();
var data_list_words = []
var id_rk = $('#data').data('id')
var id_folder = $('#data').data('fid')
var id_mf = $('#minus_frase').data('id')
var data_mf_words = []
// получаем список минус фраз
$.ajax({
 contentType: 'application/json;charset=UTF-8',
 url: "up/get_mf_words",
 type: "POST",
 data: JSON.stringify({'id_mf': id_mf}),
 success: function (resp) {

   data_mf_words = resp.mf

   if (data_mf_words.length < 50) {
     var num_control = data_mf_words.length
   } else {
     var num_control = 50
   }

   for (var n = 0; n < num_control; ++n){
     if (data_mf_words[n] == undefined){
         break;
     };
    $('tbody[name="active_words"]').append('<tr name="active_words" data-name="'+data_mf_words[n]+'" data-scroll="'+[n]+'">'+
                                              '<th class="grupirator">'+
                                                '<div class="row">'+
                                                  '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
                                                    '<img data-word="'+data_mf_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz glaz_mf" src="/static/img/eye.svg">'+
                                                  '</div>'+
                                                  '<div class="col-10 row justify-content-between active_words" data-word="'+data_mf_words[n]+'" style="padding: 0;">'+
                                                    '<div class="col-10">'+data_mf_words[n]+'</div>'+
                                                    '<div class="col-2 active_del" data-word="'+data_mf_words[n]+'" style="display:none;font-size:8px"> &#10060;</div>'+
                                                  '</div>'+
                                                '</div>'+
                                              '</th>'+
                                            '</tr>');
    }
  }
});

// получение json данных с группированными словами
$.ajax({
 contentType: 'application/json;charset=UTF-8',
 url: "up/get_data_words",
 type: "POST",
 data: JSON.stringify({'id_rk': id_rk}),
 beforeSend: function () {
  $("#preloader").addClass("visible").removeClass('hidden')
  },
 complete: function () {
    $("#preloader").addClass("hidden").removeClass('visible')
  },
 success: function (resp) {
    //  - Добавляем сегмент
    data_words = resp.data
    data_list_words = resp.list_words

    if (data_words.length < 50) {
      var num_control = data_words.length
    } else {
      var num_control = 50
    }

    for (var n = 0; n < num_control; ++n){
      if (data_words[n] == undefined){
          break;
      };
       $('tbody[name="fraze"]').append('<tr name="gruping_words" data-id='+n+' data-chas='+data_words[n][1]+'>'+
                                       '<th style="padding: 0px;">'+
                                       '<div class="row" style="margin: 0px;">'+
                                         '<div class="col-1 plus" style="padding: 13px;">'+
                                           '<div class="botton-popup" data-id="'+n+'"><div class="treygolnik-popup"></div></div>'+
                                             '<div name="dropdown" class="popup-words" data-id="'+n+'"></div>'+
                                         '</div>'+
                                         '<div class="col-8 words" data-id="'+n+'" name="words" style="padding: 10px 0;"></div>'+
                                         '<div class="col-1 glaz glaz_popup" data-id="'+n+'" name="glaz"> <img data-toggle="modal" data-target="#glaz_app" class="text-item" src="/static/img/eye.svg"> </div>'+
                                         '<div class="col-2" name="chas" style="text-align: center;padding: 10px;">'+data_words[n][1]+'</div>'+
                                        '</div>'+
                                        '</th>'+
                                        '</tr>');
      for (var i = 0; i < data_words[n][0].length; ++i){
        if (data_words[n] == undefined){
            break;
        };
        if (data_mf_words.includes(data_words[n][0][i])) {
          $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_active podcherk_active" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')

        } else {
          $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_unactive" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')
        }
      }
    }
  }
});


// ________________ Показ словосочетаний ________________

// функция уникализации словаря
function uniq(a) {
    var seen = {};
    return a.filter(function(item) {
        return seen.hasOwnProperty(item) ? false : (seen[item] = true);
    });
};

// поп-ап с похожими словами
var  data_words_duble = []
$('body').on("click", '.botton-popup', function(){
  var id = $(this).data("id");
  if ($('#poisk_words').length == 1) {
    var  data_words_duble = data_words_poisk
  } else {
    var  data_words_duble = data_words
  }

  if ($('div[name="dropdown"][data-id="'+id+'"]').hasClass('popup-open')) {
    $('div[name="dropdown"][data-id="'+id+'"]').removeClass("popup-open").addClass("popup-open2").hide()
  }
  else if ($('div[name="dropdown"][data-id="'+id+'"]').hasClass('popup-open2')) {
    $('div[name="dropdown"][data-id="'+id+'"]').addClass("popup-open").removeClass("popup-open2").show()

    //Если отмеченные слово есть в выводных словах - меняем класс
    $('.popup-words-item[data-id="'+id+'"]').each(function() {
      if (data_mf_words.indexOf( String($(this).data('word'))) != -1 )
        $(this).addClass("words_active").removeClass('words_unactive');
    });

  }
  else {
    var words_fraze = []
    for (var i = 0; i < data_words_duble[id][2].length; ++i){
      words_fraze = words_fraze.concat(data_words_duble[id][2][i][0].split(' '))
    };
    words_fraze = uniq(words_fraze);

    // Идем по полученному словарю и формируем список фраз
    var words_two = []
    var list_word = data_words_duble[id][0]
    for (var i = 0; i < list_word.length; ++i){
      for (var n = 0; n < words_fraze.length; ++n){
          if (list_word[i] !=  words_fraze[n]){
              var e = list_word[i]+' '+words_fraze[n];
              words_two.push(e);}
        };
      };

    words_two = uniq(words_two);
    $('.popup-words-item[data-id="'+id+'"]').remove();
    for (var n = 0; n < words_two.length; ++n){
      $('.popup-words[data-id="'+id+'"]').addClass("popup-open").append('<div class="popup-words-item words_unactive" data-id="'+id+'" data-word="'+words_two[n]+'">'+words_two[n]+'</div>').show();
      }

    //Если отмеченные слово есть в выводных словах - меняем класс
    $('.popup-words-item[data-id="'+id+'"]').each(function() {
      if (data_mf_words.indexOf( String($(this).data('word'))) != -1 )
        $(this).addClass("words_active").removeClass('words_unactive');
    });
  }
});

// выбор словосочетания
$('body').on("click", '.popup-words-item', function(){
  if ($(this).hasClass('words_active'))
    $(this).removeClass('words_active').addClass("words_unactive");
   else
    $(this).addClass('words_active').removeClass('words_unactive');
});


// ---------------------------      ***      ---------------------------
//                        Навигация по сегментам
$('body').on('click', '.segment_active', function(){
  $(this).addClass("segment_unactive").removeClass("segment_active");
  if ($('.segment_active').length == 0) {
    $('#all_seg').prop('checked', false);
  }
  });

$('body').on('click', '.segment_unactive', function(){
  $(this).addClass("segment_active").removeClass("segment_unactive");
  if (!$("#all_seg").prop("checked")) {
    $('#all_seg').prop('checked', true);
  }
  });

  // выбрать все
  $('body').on('click', '#all_seg', function() {
    if (!$("#all_seg").prop("checked")) {
      // скрываем
        $('.segment_active').addClass("segment_unactive").removeClass("segment_active");
    } else {
      // показываем ВЧ
        $('.segment_unactive').addClass("segment_active").removeClass("segment_unactive");
    }
  });



// отобразить сегменты
$('body').on('click', '#veiw_words', function(){
  var list_segment_active = [];
  var id = $("#data").data("id")
  $("tr[name='segment'].segment_active").each(function() {
    list_segment_active.push( $(this).attr("data") );
  });

  $.ajax({
   contentType: 'application/json;charset=UTF-8',
   url: "up/grupirator_view_segment",
   type: "POST",
   data: JSON.stringify({'list_segment_active': list_segment_active, 'id': id}),
   beforeSend: function () {
  $("#preloader").addClass("visible").removeClass('hidden')
  },
  complete: function () {
    $("#preloader").addClass("hidden").removeClass('visible')
  },
  success: function (resp) {
      //  - Добавляем сегмент
      $('tbody[name="fraze"]').replaceWith('<tbody style="background-color: #ffff;" name="fraze"></tbody>');
      data_words = resp.data
      data_list_words = resp.list_words

      if (data_words.length < 50) {
        var num_control = data_words.length
      } else {
        var num_control = 50
      }

      for (var n = 0; n < num_control; ++n){
        if (data_words[n] == undefined){
            break;
        };
         $('tbody[name="fraze"]').append('<tr name="gruping_words" data-id='+n+' data-chas='+data_words[n][1]+'>'+
                                         '<th style="padding: 0px;">'+
                                         '<div class="row" style="margin: 0px;">'+
                                           '<div class="col-1 plus" style="padding: 13px;">'+
                                             '<div class="botton-popup" data-id="'+n+'"><div class="treygolnik-popup"></div></div>'+
                                               '<div name="dropdown" class="popup-words" data-id="'+n+'"></div>'+
                                           '</div>'+
                                           '<div class="col-8 words" data-id="'+n+'" name="words" style="padding: 10px 0;"></div>'+
                                           '<div class="col-1 glaz glaz_popup" data-id="'+n+'" name="glaz"> <img data-toggle="modal" data-target="#glaz_app" class="text-item" src="/static/img/eye.svg"> </div>'+
                                           '<div class="col-2" name="chas" style="text-align: center;padding: 10px;">'+data_words[n][1]+'</div>'+
                                          '</div>'+
                                          '</th>'+
                                          '</tr>');
        for (var i = 0; i < data_words[n][0].length; ++i){
          if (data_words[n] == undefined){
              break;
          };
          if (data_mf_words.includes(data_words[n][0][i])) {
            $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_active podcherk_active" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')

          } else {
            $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_unactive" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')
          }
        }
      }
    }
  });
});

// подгрузка элементов
$('#base_words').scroll(function () {
    var control_words = $('tr[name="gruping_words"]').length - 10
    var gruping_words = $('tr[name="gruping_words"][data-id="'+control_words+'"]').offset().top;

    if( 700 > gruping_words){
      var all_words = $('tr[name="gruping_words"]').length
      if (data_words.length > all_words+1) {
        var num1 = all_words + 1
        var num50 = all_words + 50
        if (num50 > data_words.length) num50=data_words.length

        for (var n = num1; n < num50; ++n){
          if (data_words[n] == undefined){
              break;
          };
           $('tbody[name="fraze"]').append('<tr name="gruping_words" data-id='+n+' data-chas='+data_words[n][1]+'>'+
                                           '<th style="padding: 0px;">'+
                                           '<div class="row" style="margin: 0px;">'+
                                             '<div class="col-1 plus" style="padding: 13px;">'+
                                               '<div class="botton-popup" data-id="'+n+'"><div class="treygolnik-popup"></div></div>'+
                                                 '<div name="dropdown" class="popup-words" data-id="'+n+'"></div>'+
                                             '</div>'+
                                             '<div class="col-8 words" data-id="'+n+'" name="words" style="padding: 10px 0;"></div>'+
                                             '<div class="col-1 glaz glaz_popup" data-id="'+n+'" name="glaz"> <img data-toggle="modal" data-target="#glaz_app" class="text-item" src="/static/img/eye.svg"> </div>'+
                                             '<div class="col-2" name="chas" style="text-align: center;padding: 10px;">'+data_words[n][1]+'</div>'+
                                            '</div>'+
                                            '</th>'+
                                            '</tr>');
          for (var i = 0; i < data_words[n][0].length; ++i){
            if (data_words[n] == undefined){
                break;
            };
            if (data_mf_words.includes(data_words[n][0][i])) {
              $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_active podcherk_active" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')

            } else {
              $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_unactive" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')
            }
          }
        }
    }
  }
});



// ---------------------------      ***      ---------------------------
//                             Выбор ключей

//  при наведении показ иконки удалить
$("body").on('mouseenter', '.active_words', function() {
    $('.active_del[data-word="'+$(this).data('word')+'"]').show();
});

$("body").on('mouseleave', '.active_words', function() {
    $('.active_del[data-word="'+$(this).data('word')+'"]').hide();
});

//  Клик по выбранным словам
$('body').on('click', '.active_words', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else{
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }

  var words = $(this).data('word')
  $('span[data-word="'+words+'"]').addClass("words_unactive ").removeClass("words_active podcherk_active");
  $('.popup-words-item[data-word="'+words+'"]').addClass("words_unactive").removeClass("words_active");
  $('tr[name="active_words"][data-name="'+words+'"]').remove()
  data_mf_words.splice(data_mf_words.indexOf(words), 1);
});


//  Словосочения в поп-аепе

$('body').on('click', '.popup-words-item.words_unactive', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else{
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }

  $(this).addClass("words_active").removeClass("words_unactive");
  var words = $(this).data('word');
  $('tbody[name="active_words"]').prepend('<tr name="active_words" data-name="'+words+'"><th class="grupirator">'+
  '<div class="row">'+
    '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
      '<img data-word="'+words+'" data-toggle="modal" data-target="#glaz_app" class="glaz" src="/static/img/eye.svg">'+
    '</div>'+
    '<div class="col-10 row justify-content-between active_words" data-word="'+words+'" style="padding: 0;">'+
      '<div class="col-10">'+words+'</div>'+
      '<div class="col-2 active_del" data-word="'+words+'" style="display:none;font-size:8px">'+
        '&#10060;'+
      '</div>'+
    '</div>'+
  '</div>');
  data_mf_words.push(words);
});

// ________________

$('body').on('click', '.popup-words-item.words_active', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else{
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }

  $(this).addClass("words_unactive").removeClass("words_active");
  var words = $(this).data('word')
  $('tr[name="active_words"][data-name="'+words+'"]').remove()
  data_mf_words.splice(data_mf_words.indexOf(words), 1);
});


//  Клик по сгруппированным словам
var list_words = []
$('body').on('click', '.words', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else{
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }
  if ($(this).data('type') == 'poisk') {
    list_words = data_words_poisk[$(this).data('id')][0]
  } else {
    list_words = data_words[$(this).data('id')][0]
  }

  if ($('span', this).hasClass("words_unactive")) {
    for (var n = 0; n < list_words.length; ++n){
      if ($('span[data-word="'+list_words[n]+'"]').hasClass("words_unactive")) {
        $('span[data-word="'+list_words[n]+'"]').addClass("words_active podcherk_active").removeClass("words_unactive ");
        $('tbody[name="active_words"]').prepend('<tr name="active_words" data-name="'+list_words[n]+'"><th class="grupirator">'+
        '<div class="row">'+
          '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
            '<img data-word="'+list_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz" src="/static/img/eye.svg">'+
          '</div>'+
          '<div class="col-10 row justify-content-between active_words" data-word="'+list_words[n]+'" style="padding: 0;">'+
            '<div class="col-10">'+list_words[n]+'</div>'+
            '<div class="col-2 active_del" data-word="'+list_words[n]+'" style="display:none; font-size:8px">'+
              '&#10060;'+
            '</div>'+
          '</div>'+
        '</div>');
        data_mf_words.push(list_words[n]);
      }
    }
  } else {
    for (var n = 0; n < list_words.length; ++n){
      $('span[data-word="'+list_words[n]+'"]').addClass("words_unactive").removeClass("words_active podcherk_active");
      $('tr[name="active_words"][data-name="'+list_words[n]+'"]').remove()
      data_mf_words.splice(data_mf_words.indexOf(list_words[n]), 1);
    }
  }
});


// ________________ Выделение слов при наведении (в сгруппированных)

var timer;
// при наведении на неактивные
$("body").on('mouseenter', 'span[name="gruping_words"].words_unactive', function() {
  var words = $(this).data('word')

  timer = setTimeout(function () {
    if (!data_mf_words.includes(words)) {
      if ($("select[name='list_mf']").val() != "Список минус фраз") {
        $('select[name="list_mf"]').addClass('mf_need_save')
      }else{
        $('select[name="list_mf"]').addClass("control_modal_mf");
      }

      $('span[data-word="'+words+'"]').addClass("words_active podcherk_active").removeClass("words_unactive");
      $('tbody[name="active_words"]').prepend('<tr name="active_words" data-name="'+words+'"><th class="grupirator">'+
      '<div class="row">'+
        '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
          '<img data-word="'+words+'" data-toggle="modal" data-target="#glaz_app" class="glaz" src="/static/img/eye.svg">'+
        '</div>'+
        '<div class="col-10 row justify-content-between active_words" data-word="'+words+'" style="padding: 0;">'+
          '<div class="col-10">'+words+'</div>'+
          '<div class="col-2 active_del" data-word="'+words+'" style="display:none; font-size:8px">'+
            '&#10060;'+
          '</div>'+
        '</div>'+
      '</div>');
      data_mf_words.push(words);
    }
  }, 1000);
});

$("body").on('mouseleave', 'span[name="gruping_words"].words_unactive', function() {
    clearTimeout(timer);
});

// при наведении на активные
$("body").on('mouseenter', 'span[name="gruping_words"].words_active', function() {

  var words = $(this).data('word')
  timer = setTimeout(function () {
    if ($("select[name='list_mf']").val() != "Список минус фраз") {
      $('select[name="list_mf"]').addClass('mf_need_save')
    }else{
      $('select[name="list_mf"]').addClass("control_modal_mf");
    }

    $('span[data-word="'+words+'"]').addClass("words_unactive ").removeClass("words_active podcherk_active");
    $('tr[name="active_words"][data-name="'+words+'"]').remove()
    data_mf_words.splice(data_mf_words.indexOf(words), 1);
  }, 1000);

});

$("body").on('mouseleave', 'span[name="gruping_words"].words_active', function() {
    clearTimeout(timer);
});



// ______________________* Отображение ключей в поп-апе *______________________ //
var list_fraze = []
$('body').on('click', '.glaz', function(){
  list_fraze = []
  $('tbody[name="fraze_glaz"]').replaceWith('<tbody style="background-color: #ffff;" name="fraze_glaz"></tbody>')
  var id = $(this).data('id')
  // провряем запустили из групп слов или из списка мину фраз
  if (id == undefined) {
    var word = $(this).data('word')
    // Получаем список фраз из словаря и сортируем их
    for (var n = 0; n < data_words.length; ++n){
        if (data_words[n][0].includes(word)) {
          list_fraze = data_words[n][2]
          // сортировка
          list_fraze = list_fraze.sort(function(a,b) {
              return b[1]-a[1]});
          break
        }
    }
  } else {
    // Получаем список фраз из словаря и сортируем их
    if ($(this).data('type') == 'poisk') {
      list_fraze = data_words_poisk[id][2]
    } else {
      list_fraze = data_words[id][2]
    }
      // сортировка
      list_fraze = list_fraze.sort(function(a,b) {
          return b[1]-a[1]});
  }

  if (list_fraze.length>0) {
    // Идем по полученному словарю и выводим фраза-частота
    if (list_fraze.length < 50) {
      var num_control = list_fraze.length
    } else {
        var num_control = 50
    }
    for (var num= 0; num < num_control; ++num) {
      var words = list_fraze[num][0].split(' ');
      var fraze_for_words = ''

      if(data_mf_words.length == 0){
        for (var n = 0; n < words.length; ++n){
          fraze_for_words += '<span class="w-curs words_unactive" data-word="'+words[n]+'">'+words[n]+'</span>'+'  ';
        }
      }else {
        for (var n = 0; n < words.length; ++n){
          var class_fraz = "words_unactive";
          if (data_mf_words.indexOf(words[n]) != -1 )
              {class_fraz = "words_active podcherk_active";}
          fraze_for_words += '<span class="w-curs '+class_fraz+'" data-word="'+words[n]+'">'+words[n]+'</span>'+'  ';
        }
      }

      $('tbody[name="fraze_glaz"]').append('<tr data-scroll="'+num+'" name="glaz_fraze" class="words-popup" data-chas="'+list_fraze[num][1]+'">'+
            '<th>'+
            '<div class="row">'+
              '<div class="col-9" name="words">'+fraze_for_words+'</div>'+
              '<div class="col-2" name="chas" style="text-align: center;">'+list_fraze[num][1]+'</div>'+
            '</div>'+
             '</th>'+
             '</tr>');
      }
  }
});

// подгрузка элементов
$('#glaz_app').scroll(function () {
    var control_words = $('tr[name="glaz_fraze"]').length - 10
    var gruping_words = $('tr[name="glaz_fraze"][data-scroll="'+control_words+'"]').offset().top;

    if( 700 > gruping_words){
      var all_words = $('tr[name="glaz_fraze"]').length
      if (list_fraze.length > all_words+1) {
        var num1 = all_words + 1
        var num50 = all_words + 50
        if (num50 > list_fraze.length) num50=list_fraze.length

        // берем отмеченные слова
        for (var num= num1; num < num50; ++num) {
          var words = list_fraze[num][0].split(' ');
          var fraze_for_words = ''
          if(data_mf_words.length == 0){
            for (var n = 0; n < words.length; ++n){
              fraze_for_words += '<span class="w-curs words_unactive " data-word="'+words[n]+'">'+words[n]+'</span>'+'  ';
            }
          }else {
            for (var n = 0; n < words.length; ++n){
              var class_fraz = "words_unactive";
              if (data_mf_words.indexOf(words[n]) != -1 )
                  {class_fraz = "words_active podcherk_active";}
              fraze_for_words += '<span class="w-curs '+class_fraz+'" data-word="'+words[n]+'">'+words[n]+'</span>'+'  ';
            }
          }

          $('tbody[name="fraze_glaz"]').append('<tr data-scroll="'+num+'" name="glaz_fraze" class="words-popup" data-chas="'+list_fraze[num][1]+'">'+
                '<th>'+
                '<div class="row">'+
                  '<div class="col-9" name="words">'+fraze_for_words+'</div>'+
                  '<div class="col-2" name="chas" style="text-align: center;">'+list_fraze[num][1]+'</div>'+
                '</div>'+
                 '</th>'+
                 '</tr>');
          }

    }
  }
});

// подгрузка элементов в минус фразы
$('#minus_frase').scroll(function () {
    var control_words = $('tr[name="active_words"]').length - 10
    var gruping_words = $('tr[name="active_words"][data-scroll="'+control_words+'"]').offset().top;

    if( 700 > gruping_words){
      var all_words = $('tr[name="active_words"]').length
      if (data_mf_words.length > all_words+1) {
        var num1 = all_words + 1
        var num50 = all_words + 50
        if (num50 > data_mf_words.length) num50=data_mf_words.length

        for (var n = num1; n < num50; ++n){
          if (data_mf_words[n] == undefined){
              break;
          };
          $('tbody[name="active_words"]').append('<tr name="active_words" data-name="'+data_mf_words[n]+'" data-scroll="'+[n]+'">'+
                                                    '<th class="grupirator">'+
                                                      '<div class="row">'+
                                                        '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
                                                          '<img data-word="'+data_mf_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz glaz_mf" src="/static/img/eye.svg">'+
                                                        '</div>'+
                                                        '<div class="col-10 row justify-content-between active_words" data-word="'+data_mf_words[n]+'" style="padding: 0;">'+
                                                          '<div class="col-10">'+data_mf_words[n]+'</div>'+
                                                          '<div class="col-2 active_del" data-word="'+data_mf_words[n]+'" style="display:none;font-size:8px"> &#10060;</div>'+
                                                        '</div>'+
                                                      '</div>'+
                                                    '</th>'+
                                                  '</tr>');

        }
    }
  }
});


// ________________показ/скрытие глаза
$("body").on('mouseenter', 'tr[name="gruping_words"]', function() {
    $('.glaz_popup[data-id="'+$(this).data('id')+'"]').show();
});
$("body").on('mouseleave', 'tr[name="gruping_words"]', function() {
    $('.glaz_popup[data-id="'+$(this).data('id')+'"]').hide();
});


// ________________ клик по словам в поп-апе
// по неактивным - добавляем в список
$('body').on('click', 'span.words_unactive', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else {
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }

  var words = $(this).data('word')

  $('span[data-word="'+words+'"]').addClass("words_active").removeClass("words_unactive");
  $('span[data-word="'+words+'"]').addClass("podcherk_active").removeClass("");

  $('tbody[name="active_words"]').prepend('<tr name="active_words" data-name="'+words+'"><th class="grupirator">'+
  '<div class="row">'+
    '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
      '<img data-word="'+words+'" data-toggle="modal" data-target="#glaz_app" class="glaz" src="/static/img/eye.svg">'+
    '</div>'+
    '<div class="col-10 row justify-content-between active_words" data-word="'+words+'" style="padding: 0;">'+
      '<div class="col-10">'+words+'</div>'+
      '<div class="col-2 active_del" data-word="'+words+'" style="display:none;font-size:8px">'+
        '&#10060;'+
      '</div>'+
    '</div>'+
  '</div>');

  $('div[data-word="'+words+'"]').addClass("words_active").removeClass("words_unactive");
  data_mf_words.push(words);
});

// по активным - удаляем из списка
$('body').on('click', 'span.words_active', function(){
  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    $('select[name="list_mf"]').addClass('mf_need_save')
  }else{
    $('select[name="list_mf"]').addClass("control_modal_mf");
  }

  var words = $(this).data('word');
  $('span[data-word="'+words+'"]').addClass("words_unactive").removeClass("words_active");
  $('span[data-word="'+words+'"]').addClass("").removeClass("podcherk_active");


  $('tr[name="active_words"][data-name="'+words+'"]').remove()
  $('div[data-word="'+words+'"]').addClass("words_unactive").removeClass("words_active");
  data_mf_words.splice(data_mf_words.indexOf(words), 1);
});


//  ________________ Удаление  запросов________________
$('body').on('click','#delete', function() {
   $(".limit-no-del").remove()
});

$('body').on('click','#but-delete', function() {
 if (data_mf_words.length > 0) {
   // создаем списки выделенных сегментов/групп/фраз
   var id = $("#data").data("id")
   var list_segment_active = [];
   $("tr[name='segment'].segment_active").each(function() {
     list_segment_active.push( $(this).attr("data") );
   });

   var nch = $('#data').data('nch');
   $.ajax({
     contentType: 'application/json;charset=UTF-8',
     url: "up/grupirator_delete_words",
     type: "POST",
     data: JSON.stringify({'nch':nch, 'id' : id, 'arr_words' : data_mf_words, 'list_segment_active':list_segment_active}),
     beforeSend: function () {
     $("#delet_app").modal("hide");
     $("#preloader").addClass("visible").removeClass('hidden')
     },
     complete: function () {
       $("#delet_app").modal("hide")
      $("#preloader").addClass("hidden").removeClass('visible')
     },
     success: function () {
       var rk_id = $('#data').data('id');
       var folder_id = $('#data').data('fid');
       if (window.location.href.split('/')[3] == "rk_ads") {
         document.location.href = 'https://shinta.ru/rk_ads/grupirator/'+folder_id+'_'+rk_id;
       } else {
         document.location.href = 'https://shinta.ru/rk_yd/grupirator/'+folder_id+'_'+rk_id;
       }
     }
   });
 } else {
   $('#modal_del').append('<div class="col limit-no-del">'+
   '<span>Нечего удалять. Не понятно что делать? Пишите в телеграм @chat_masa</span></div>');
 }

});


//  ________________ Перенос запросов ________________

// Выбор при клике rk
$('body').on('click', '.rk_unactive', function() {
  $('.limit-no').remove()
  $('.rk_active').addClass("rk_unactive").removeClass("rk_active");
  $(this).addClass("rk_active").removeClass("rk_unactive");
  $('div[name="in_segment"]').show();
  $('input[name="in_segment"]').show();

  var id_rk = $(this).data("id");
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/grupirator_perenos_veiw_segment",
    type: "POST",
    data: JSON.stringify({'id_rk':id_rk }),
    success: function (resp) {
      // Выводим навигацию
      $('div[name="new_rk"]').hide();
      $('tbody[name="perenos_segment_veiw"]').replaceWith(resp.data);
      $('div[name="new_segment"]').show();
    }
  });

});

$('body').on('click', '.rk_active', function() {
  $(this).addClass("rk_unactive").removeClass("rk_active");

  $('div[name="new_rk"]').show();
  $('div[name="new_segment"]').hide();
});


// гуляние по папкам
$('body').on('click', '.folder', function() {
  var id_folder = $(this).data("id");
  var rk_type = $('div[name="perenos_table"]').data('type')
  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/grupirator_perenos",
    type: "POST",
    data: JSON.stringify({'id_folder':id_folder, 'rk_type':rk_type }),
    success: function (resp) {
      // Выводим навигацию
    $('div[name="perenos_table"]').replaceWith(resp.data);

    }
  });
});

// выбор сегментов
$('body').on('click', '.seg_unactive', function() {
  $('.limit-no').remove()
  $('.seg_active').addClass("seg_unactive").removeClass("seg_active");
  $(this).addClass("seg_active").removeClass("seg_unactive");

  $('div[name="in_segment"]').hide();
  $('input[name="in_segment"]').hide();
});
$('body').on('click', '.seg_active', function() {
  $(this).addClass("seg_unactive").removeClass("seg_active");

  $('div[name="in_segment"]').show();
  $('input[name="in_segment"]').show();
});


//________________ собственно сам перенос
$('body').on('click','#perenos-words', function() {

  // создаем списки выделенных сегментов/групп/фраз
  var rk_id = $("#data").data("id")
  var name_rk = $("#data").data("name")
  var id_folder = $('.xleb_activ_cp').data('id');
  var chastota = $('#data').data('nch');
  var rk_type = $('div[name="perenos_table"]').data('type')

  var list_segment_active = [];
  $("tr[name='segment'].segment_active").each(function() {
    list_segment_active.push( $(this).attr("data") );
  });

  var arr_words = data_list_words.filter(value => data_mf_words.includes(value))

  //
  var id_seg = ''
  var name_rk = ''
  var name_segment = ''
  var rk_id_kuda = ''

  id_seg = $('.seg_active').data("id");
  name_rk = $('input[name="new_rk"]').val();
  name_segment = $('input[name="in_segment"]').val();
  rk_id_kuda = $(".rk_active").data("id")


  // если выбран сегмент - переносим в сегмент
  if (id_seg != undefined && rk_id_kuda !=undefined) {
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/grupirator_perenos_words",
      type: "POST",
      data: JSON.stringify({'rk_type' : rk_type, 'rk_id_kuda':rk_id_kuda, 'id_seg' : id_seg, 'rk_id' : rk_id, 'list_segment_active':list_segment_active, 'id_folder':id_folder, 'arr_words' : arr_words, 'name_segment':name_segment, 'name_rk':name_rk, 'chastota': chastota}),
      beforeSend: function () {
      $("#perenosModal").modal("hide")
      $("#preloader").addClass("visible").removeClass('hidden')
      },
      complete: function () {
       $("#preloader").addClass("hidden").removeClass('visible')
      },
      success: function () {
        var rk_id = $('#data').data('id');
        var folder_id = $('#data').data('fid');
        if (window.location.href.split('/')[3] == "rk_ads") {
          document.location.href = 'https://shinta.ru/rk_ads/grupirator/'+folder_id+'_'+rk_id;
        } else {
          document.location.href = 'https://shinta.ru/rk_yd/grupirator/'+folder_id+'_'+rk_id;
        }
      }
    });
  }
  // если указано имя сегмента
  else if (name_segment.length > 0) {
    id_seg = ''
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/grupirator_perenos_words",
      type: "POST",
      data: JSON.stringify({'rk_type' : rk_type, 'rk_id' : rk_id, 'rk_id_kuda':rk_id_kuda, 'id_folder':id_folder, 'arr_words' : data_mf_words, 'list_segment_active':list_segment_active, 'id_seg':id_seg, 'name_segment':name_segment, 'name_rk':name_rk, 'chastota': chastota}),
      beforeSend: function () {
      $("#perenosModal").modal("hide")
      $("#preloader").addClass("visible").removeClass('hidden')
      },
      complete: function () {
       $("#preloader").addClass("hidden").removeClass('visible')
      },
      success: function () {
        var rk_id = $('#data').data('id');
        var folder_id = $('#data').data('fid');
        if (window.location.href.split('/')[3] == "rk_ads") {
          document.location.href = 'https://shinta.ru/rk_ads/grupirator/'+folder_id+'_'+rk_id;
        } else {
          document.location.href = 'https://shinta.ru/rk_yd/grupirator/'+folder_id+'_'+rk_id;
        }
      }
    });
  }
  // если указано имя рк
  else if (name_rk.length > 0) {
    id_seg = ''
    var id_folder = $('.xleb_activ_cp').data("id");
    rk_id_kuda = ''
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/grupirator_perenos_words",
      type: "POST",
      data: JSON.stringify({'rk_id' : rk_id, 'rk_id_kuda' : rk_id_kuda, 'arr_words' : data_mf_words, 'id_seg':id_seg, 'name_segment':name_segment, 'name_rk':name_rk, 'id_folder':id_folder, 'list_segment_active':list_segment_active, 'rk_type':rk_type, 'chastota': chastota}),
      beforeSend: function () {
      $("#perenosModal").modal("hide")
      $("#preloader").addClass("visible").removeClass('hidden')
      },
      complete: function () {
       $("#preloader").addClass("hidden").removeClass('visible')
      },
      success: function () {
        var rk_id = $('#data').data('id');
        var folder_id = $('#data').data('fid');
        if (window.location.href.split('/')[3] == "rk_ads") {
          document.location.href = 'https://shinta.ru/rk_ads/grupirator/'+folder_id+'_'+rk_id;
        } else {
          document.location.href = 'https://shinta.ru/rk_yd/grupirator/'+folder_id+'_'+rk_id;
        }
      }
    });
  }
  // иначе
  else {
    $('div[name="perenos_table"]').append('<div class="col limit-no">'+
    '<span>Выберите РК и сегмент куда переносить или дайте новому имя. Если не понятно - пишите в телеграм @chat_masa</span></div>');
    setTimeout(function(){$('.limit-no').fadeOut('slow')},10000);

  }

});


// ________________ Filter POP-UP ________________

$('body').on('click','.filtet_unactive', function() {
  $(this).attr("src", "/static/img/funnel2.svg");
   $('.filtet_popup').show('slow')
   $(this).addClass('filtet_active').removeClass('filtet_unactive')
});

$('body').on('click','.filtet_active', function() {
  $(this).attr("src", "/static/img/funnel.svg");
   $('.filtet_popup').hide('slow')
   $(this).addClass('filtet_unactive').removeClass('filtet_active')
});


//  ________________ Сортаировка ________________

$('body').on('click','.dropdown-item', function() {
  // Очищаем таблицу
  $('tr[name="gruping_words"]').remove();

  if (!$(this).hasClass('active')) {
    if ($(this).attr('name') == '10') {
      $('#sort').attr('src', '/static/img/sort-9-1.svg');

      // От 1 до 1000...
      data_words.sort(function(a,b) {
          return b[1]-a[1]});
    }
    else if ($(this).attr('name') == '01') {
      $('#sort').attr('src', '/static/img/sort-1-9.svg');

     // От 1000.... до 1
     data_words.sort(function(a,b) {
         return a[1]-b[1]});
    }
    else if ($(this).attr('name') == 'az') {
      $('#sort').attr('src', '/static/img/sort-a-z.svg');

       // От А до я
       data_words.sort(function(a, b){
           if(a[0] < b[0]) { return -1; }
           if(a[0] > b[0]) { return 1; }
           return 0;
       })
    }
    else if ($(this).attr('name') == 'za') {
      $('#sort').attr('src', '/static/img/sort-z-a.svg');

       // Я до а
       data_words.sort(function(a, b){
           if(a[0] > b[0]) { return -1; }
           if(a[0] < b[0]) { return 1; }
           return 0;
       })
    }
  }

  $('.dropdown-item').removeClass('active')
  $(this).addClass('active');

// вывод данных
  if (data_words.length < 50) {
    var num_control = data_words.length
  } else {
    var num_control = 50
  }

  for (var n = 0; n < num_control; ++n){
    if (data_words[n] == undefined){
        break;
    };
     $('tbody[name="fraze"]').append('<tr name="gruping_words" data-id='+n+' data-chas='+data_words[n][1]+'>'+
                                     '<th style="padding: 0px;">'+
                                     '<div class="row" style="margin: 0px;">'+
                                       '<div class="col-1 plus" style="padding: 13px;">'+
                                         '<div class="botton-popup" data-id="'+n+'"><div class="treygolnik-popup"></div></div>'+
                                           '<div name="dropdown" class="popup-words" data-id="'+n+'"></div>'+
                                       '</div>'+
                                       '<div class="col-8 words" data-id="'+n+'" name="words" style="padding: 10px 0;"></div>'+
                                       '<div class="col-1 glaz glaz_popup" data-id="'+n+'" name="glaz"> <img data-toggle="modal" data-target="#glaz_app" class="text-item" src="/static/img/eye.svg"> </div>'+
                                       '<div class="col-2" name="chas" style="text-align: center;padding: 10px;">'+data_words[n][1]+'</div>'+
                                      '</div>'+
                                      '</th>'+
                                      '</tr>');
    for (var i = 0; i < data_words[n][0].length; ++i){
      if (data_words[n] == undefined){
          break;
      };
      if (data_mf_words.includes(data_words[n][0][i])) {
        $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_active podcherk_active" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')

      } else {
        $('.words[name="words"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words[n][0][i]+' data-id='+n+' class="words_unactive" style="font-family: \'Roboto Mono\', monospace;"> '+data_words[n][0][i]+' </span>')
      }
    }
  }
});


//             ________________ Поиск ________________

$('body').on('click','#button-poisk', function() {
  $('.del_poisk').show();
  $('tbody[name="poisk"]').remove();

  var text = $('input[name="poisk"]').val();
  var id = $("#data").data("id")
  var list_segment_active = [];
  $("tr[name='segment'].segment_active").each(function() {
    list_segment_active.push( $(this).attr("data") );
  });

  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/grupirator_poisk",
    type: "POST",
    data: JSON.stringify({'id' : id, 'text' : text, 'list_segment_active':list_segment_active}),
    beforeSend: function () {
    $("#preloader").addClass("visible").removeClass('hidden')
    },
    complete: function () {
     $("#preloader").addClass("hidden").removeClass('visible')
    },
    success: function (resp) {
       //  - Добавляем сегмент
       $('#base_words').hide();
       $('.col-6.dannie2').append('<div class="dannie" id="poisk_words">'+
                                       '<table name="fraze" class="table table-bordered table-sm" style="font-size: 14px;">'+
                                       '<tbody style="background-color: #ffff;" name="poisk"></tbody>'+
                                     '</table>'+
                                   '</div>')
       data_words_poisk = resp.data;

       //  - Добавляем сегмент
       for (var n = 0; n < data_words_poisk.length; ++n){
          $('tbody[name="poisk"]').append('<tr class="data_words_poisk" name="gruping_words" data-id='+n+' data-chas='+data_words_poisk[n][1]+'>'+
                                          '<th style="padding: 0px;">'+
                                          '<div class="row" style="margin: 0px;">'+
                                            '<div class="col-1 plus" style="padding: 13px;">'+
                                              '<div class="botton-popup" data-id="'+n+'"><div class="treygolnik-popup"></div></div>'+
                                                '<div name="dropdown" class="popup-words" data-id="'+n+'"></div>'+
                                            '</div>'+
                                            '<div class="col-8 words" data-type="poisk" data-id="'+n+'" name="words_poisk" style="padding: 10px 0;"></div>'+
                                            '<div class="col-1 glaz glaz_popup" data-id="'+n+'" name="glaz" data-type="poisk"> <img data-toggle="modal" data-target="#glaz_app" class="text-item" src="/static/img/eye.svg"> </div>'+
                                            '<div class="col-2" name="chas" style="text-align: center;padding: 10px;">'+data_words_poisk[n][1]+'</div>'+
                                           '</div>'+
                                           '</th>'+
                                           '</tr>');
         for (var i = 0; i < data_words_poisk[n][0].length; ++i){
           if (data_words_poisk[n] == undefined){
               break;
           };
           if (data_mf_words.includes(data_words_poisk[n][0][i])) {
             $('.words[name="words_poisk"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words_poisk[n][0][i]+' data-id='+n+' class="words_active podcherk_active" style="font-family: \'Roboto Mono\', monospace;"> '+data_words_poisk[n][0][i]+' </span>')

           } else {
             $('.words[name="words_poisk"][data-id="'+n+'"]').append('<span name="gruping_words" data-word='+data_words_poisk[n][0][i]+' data-id='+n+' class="words_unactive" style="font-family: \'Roboto Mono\', monospace;"> '+data_words_poisk[n][0][i]+' </span>')
           }
         }
       }
     }
   });
});


$('body').on('click','.del_poisk', function() {
  $('.del_poisk').hide();
  $('#poisk_words').remove()
  $('#base_words').show();

});


//            *** ________________ Минус фразы ________________ ***

// ________________ проверка
$('body').on('click', 'img[data-target="#minus_fraze_popup"]', function(){
  $('textarea[name="minus_words"]').text('')

  // 1. Формируем массив отмеченных слов и добавляем их в новый список
  for (var n = 0; n <data_mf_words.length; ++n){
   $('textarea[name="minus_words"]').append(data_mf_words[n]+"\n")
   }

  if ($("select[name='list_mf'] :selected").val() == "Список минус фраз") {
// скрываем таблицу добавления фраз
    $('div[data-name="add_mf_words"]').hide()
// если добавление неактивно то активируем его
    if ($('div[data-name="add_mf"][name="panel_mf"]').hasClass('nav-unactiv')) {
      $('div[data-name="add_mf"]').show()
      $('div[data-name="add_mf"][name="panel_mf"]').addClass('nav-activ').removeClass('nav-unactiv')
    }
  }else {
    $('div[data-name="add_mf_words"][name="panel_mf"]').show()

    var id_mf = $(this).data('idmf')
    $('button[name="button_mf"]').attr("data-idmf", id_mf)
  }
});

// ________________ вывод списка
// предупреждение
$('body').on('click', '.control_modal_mf', function() {
  if (data_mf_words.length > 0) {
    $('#modal_varning_mf').modal('show')
  }
});

// ________________ забыл сохранить
$('body').on('click', '.mf_need_save', function() {
    $('#mf_need_save').modal('show')
});

$('body').on('click', '#no_save_mf', function() {
    $('select[name="list_mf"]').removeClass('mf_need_save')
    $('#mf_need_save').modal('hide')
});


$('body').on('click', '#yes_seve_mf', function() {
    $('#mf_need_save').modal('hide')
    var folder_id = $("#data").data("fid")
    var id_rk = $("#data").data("id")

    var id_mf = $("select[name='list_mf'] :selected").data("id");

    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/save_mf",
      type: "POST",
      data: JSON.stringify({'folder_id':folder_id, 'id_mf' : id_mf, 'id_rk':id_rk, 'mf_list':data_mf_words}),
      success: function (resp) {
        $('.save2').show('slow');
        setTimeout(function(){$('.save2').fadeOut('slow')},2000);
        $('select[name="list_mf"]').removeClass('mf_need_save')
     }
    });
});


//________________ сменить списка минус фраз
$('select[name="list_mf"]').change(function() {

  if ($("select[name='list_mf']").val() != "Список минус фраз") {
    var id_mf = $('select[name="list_mf"] :selected').data("id")
    $('img[data-target="#minus_fraze_popup"]').attr("data-idmf", id_mf)

    $('img[name="del_mf"]').show()
    $('img[name="save_mf"]').show()
    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/get_mf_words",
      type: "POST",
      data: JSON.stringify({'id_mf' : id_mf}),
      success: function (resp) {
        $('select[name="list_mf"]').removeClass("control_modal_mf");name="active_words"
        $('tr[name="active_words"]').remove();
// снимаем отметку со всех выделенных слов
        $('span[name="gruping_words"]').addClass("words_unactive ").removeClass("words_active podcherk_active");

        data_mf_words = resp.mf
        if (data_mf_words.length < 50) {
          var num_control = data_mf_words.length
        } else {
          var num_control = 50
        }

        for (var n = 0; n < num_control; ++n){
          if (data_mf_words[n] == undefined){
              break;
          };
         $('tbody[name="active_words"]').append('<tr name="active_words" data-name="'+data_mf_words[n]+'" data-scroll="'+[n]+'">'+
                                                   '<th class="grupirator">'+
                                                     '<div class="row">'+
                                                       '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
                                                         '<img data-word="'+data_mf_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz glaz_mf" src="/static/img/eye.svg">'+
                                                       '</div>'+
                                                       '<div class="col-10 row justify-content-between active_words" data-word="'+data_mf_words[n]+'" style="padding: 0;">'+
                                                         '<div class="col-10">'+data_mf_words[n]+'</div>'+
                                                         '<div class="col-2 active_del" data-word="'+data_mf_words[n]+'" style="display:none;font-size:8px"> &#10060;</div>'+
                                                       '</div>'+
                                                     '</div>'+
                                                   '</th>'+
                                                 '</tr>');
         }
// ставим отметку для всех слов из полученного списка
      $('span[name="gruping_words"]').each(function() {
      	if (data_mf_words.indexOf( String($(this).data('word')) ) != -1 ){
           $(this).addClass("words_active podcherk_active").removeClass("words_unactive ");
        }
      });
   }
  });
}
  else {
    $('img[name="del_mf"]').hide()
    $('img[name="save_mf"]').hide()

    $('select[name="list_mf"]').addClass("control_modal_mf");

// удаляем id-кнопки в попапе + удаляем таблицу минус фраз
    $('img[data-target="#minus_fraze_popup"]').attr("data-idmf", '');
    $('tr[name="active_words"]').remove();

// снимаем отметку со всех выделенных слов
    $('span[name="gruping_words"]').addClass("words_unactive ").removeClass("words_active podcherk_active");
  }
});

// предупреждение минус фраз
$('body').on('click','#yes_varning_mf', function() {
  $('select[name="list_mf"]').removeClass("control_modal_mf");
  $('#modal_varning_mf').modal('hide')
});

// ________________ навигация минус фразы

// переход на добавление фраз
$('body').on('click','div[data-name="add_mf_words"]', function() {
  if ($(this).hasClass('nav-unactiv')) {
    var name = $(this).data('name')
    $('div[name="panel_mf"]').addClass('nav-unactiv').removeClass('nav-activ')
    $('div[name="modal_mf"]').hide()

    $('div[name="panel_mf"][data-name="'+name+'"]').addClass('nav-activ').removeClass('nav-unactiv')
    $('div[name="modal_mf"][data-name="'+name+'"]').show()

// меняем id и текст у кнопки на "добавление фраз"
    $('button[name="button_mf"]').attr("id", 'add_mf_words').html('Добавить запросы');
  }
});

// переход на добавление списка минус фраз
$('body').on('click','div[data-name="add_mf"]', function() {
  if ($(this).hasClass('nav-unactiv')) {
    var name = $(this).data('name')
    $('div[name="panel_mf"]').addClass('nav-unactiv').removeClass('nav-activ')
    $('div[name="modal_mf"]').hide()

    $('div[name="panel_mf"][data-name="'+name+'"]').addClass('nav-activ').removeClass('nav-unactiv')
    $('div[name="modal_mf"][data-name="'+name+'"]').show()

// меняем id и текст у кнопки на "добавление списка минус фраз"
    $('button[name="button_mf"]').attr("id", 'add_mf').html('Создать список');
  }
});

// ________________ создание
$('body').on('click', '#add_mf', function(){
  var name = $('input[name="name_minus"]').val()
  var words_list = $('textarea[name="minus_words"]').val().replace(/[><№;+%.$!@#^&*()}{'|/?[\],\\=]/g,'').split("\n");
  var id_rk = $("#data").data("id")

  // удаляем пустые строки
  for (var i = 0; i < words_list.length; ++i){
            if (words_list[i]== '') {
            words_list.splice(i, 1);
            continue
                }
            }

  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/create_minus_frase",
    type: "POST",
    data: JSON.stringify({'id_rk' : id_rk, 'name' : name, 'words_list':words_list}),
    success: function (resp) {
      $('select[name="list_mf"]').removeClass('control_modal_mf')
      $('#minus_fraze_popup').modal('hide')
      // отобразить в списке
      $('select[name="list_mf"]').append(resp.mf);
      $('img[name="del_mf"]').show()
      $('img[name="save_mf"]').show()

      $('option[data-id="'+resp.id_mf+'"]').attr('selected', '')
      // отображаем слова
      $('tr[name="active_words"]').remove();
      data_mf_words = resp.data
      if (data_mf_words.length < 50) {
        var num_control = data_mf_words.length
      } else {
        var num_control = 50
      }

      for (var n = 0; n < num_control; ++n){
        if (data_mf_words[n] == undefined){
            break;
        };
       $('tbody[name="active_words"]').append('<tr name="active_words" data-name="'+data_mf_words[n]+'" data-scroll="'+[n]+'">'+
                                                 '<th class="grupirator">'+
                                                   '<div class="row">'+
                                                     '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
                                                       '<img data-word="'+data_mf_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz glaz_mf" src="/static/img/eye.svg">'+
                                                     '</div>'+
                                                     '<div class="col-10 row justify-content-between active_words" data-word="'+data_mf_words[n]+'" style="padding: 0;">'+
                                                       '<div class="col-10">'+data_mf_words[n]+'</div>'+
                                                       '<div class="col-2 active_del" data-word="'+data_mf_words[n]+'" style="display:none;font-size:8px"> &#10060;</div>'+
                                                     '</div>'+
                                                   '</div>'+
                                                 '</th>'+
                                               '</tr>');
       }
// снимаем отметку со всех выделенных слов
      $('span[name="gruping_words"]').addClass("words_unactive ").removeClass("words_active podcherk_active");

  // ставим отметку для всех слов из полученного списка
      $('span[name="gruping_words"]').each(function() {
        if (data_mf_words.indexOf( String($(this).data('word')) ) != -1 ){
           $(this).addClass("words_active podcherk_active").removeClass("words_unactive ");
        }
      });
   }
  });

});

// ________________ добавление фраз в текущий
$('body').on('click', '#add_mf_words', function(){
  var words_list = $('textarea[name="add_words_mf"]').val().split("\n");
  var id_mf = $("select[name='list_mf'] :selected").data("id");

  // удаляем пустые строки
  for (var i = 0; i < words_list.length; ++i){
            if (words_list[i]== '') {
            words_list.splice(i, 1);
            continue
                }
            }

  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/add_words_mf",
    type: "POST",
    data: JSON.stringify({'id_mf' : id_mf, 'words_list':words_list}),
    success: function (resp) {
      $('#minus_fraze_popup').modal('hide')

      // отображаем слова
      $('tr[name="active_words"]').remove();
      data_mf_words = resp.data
      if (data_mf_words.length < 50) {
        var num_control = data_mf_words.length
      } else {
        var num_control = 50
      }

      for (var n = 0; n < num_control; ++n){
        if (data_mf_words[n] == undefined){
            break;
        };
       $('tbody[name="active_words"]').append('<tr name="active_words" data-name="'+data_mf_words[n]+'" data-scroll="'+[n]+'">'+
                                                 '<th class="grupirator">'+
                                                   '<div class="row">'+
                                                     '<div class="col-2" style="padding: 0;text-align: center;margin-left: 5px;">'+
                                                       '<img data-word="'+data_mf_words[n]+'" data-toggle="modal" data-target="#glaz_app" class="glaz glaz_mf" src="/static/img/eye.svg">'+
                                                     '</div>'+
                                                     '<div class="col-10 row justify-content-between active_words" data-word="'+data_mf_words[n]+'" style="padding: 0;">'+
                                                       '<div class="col-10">'+data_mf_words[n]+'</div>'+
                                                       '<div class="col-2 active_del" data-word="'+data_mf_words[n]+'" style="display:none;font-size:8px"> &#10060;</div>'+
                                                     '</div>'+
                                                   '</div>'+
                                                 '</th>'+
                                               '</tr>');
       }
// снимаем отметку со всех выделенных слов
      $('span[name="gruping_words"]').addClass("words_unactive ").removeClass("words_active podcherk_active");

  // ставим отметку для всех слов из полученного списка
      $('span[name="gruping_words"]').each(function() {
        if (data_mf_words.indexOf( String($(this).data('word')) ) != -1 ){
           $(this).addClass("words_active podcherk_active").removeClass("words_unactive ");
        }
      });

      // очищаем поле ввода новых минус фраз в поп-апе
      $('textarea[name="add_words_mf"]').val('')

   }
  });

});


// ________________ удаление минус фраз

// удаление списка
$('body').on('click', 'img[name="del_mf"]', function(){
  $('#modal_varning').modal('show')
});

$('body').on('click', '#yes_del_mf', function(){
    var id_mf = $("select[name='list_mf'] :selected").data("id");
    var id_rk = $("#data").data("id")
    var id_folder = $("#data").data("fid")

    $.ajax({
      contentType: 'application/json;charset=UTF-8',
      url: "up/del_mf",
      type: "POST",
      data: JSON.stringify({'id_mf' : id_mf, 'id_rk' : id_rk, 'id_folder' : id_folder}),
      success: function (resp) {
        data_mf_words = []
        $('#modal_varning').modal('hide')

        var id_mf = $("select[name='list_mf'] :selected").data("id");
// удаляем списоr минус фраз и выведенную таблицу слов
        $('tr[name="active_words"]').remove();
        $('option[name="name_mf"][data-id="'+id_mf+'"]').remove()

// переключаем выбор списка на начальный
        $('#nach_mf').attr('selected', '')

        $('img[name="del_mf"]').hide()
        $('img[name="save_mf"]').hide()

// если была отметка что нужно сохранить - убираем ее
        $('.custom-select').removeClass('mf_need_save')

// снимаем отметку со всех выделенных слов
        $('span[name="gruping_words"]').addClass("words_unactive ").removeClass("words_active podcherk_active");
     }
    });
});


// сохранение списка минуф фраз за рк
$('body').on('click', 'img[name="save_mf"]', function(){

  var folder_id = $("#data").data("fid")
  var id_rk = $("#data").data("id")
  var id_mf = $("select[name='list_mf'] :selected").data("id");

  $.ajax({
    contentType: 'application/json;charset=UTF-8',
    url: "up/save_mf",
    type: "POST",
    data: JSON.stringify({'folder_id':folder_id, 'id_mf' : id_mf, 'id_rk':id_rk, 'mf_list':data_mf_words}),
    success: function (resp) {
      $('.save2').show('slow');
      setTimeout(function(){$('.save2').fadeOut('slow')},2000);
      $('select[name="list_mf"]').removeClass('mf_need_save')
   }
  });

});
