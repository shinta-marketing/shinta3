from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, send_file
import json
import bson
from bson.objectid import ObjectId

from models import *
from main import *

import difflib
from difflib import get_close_matches
import pymorphy2

from operator import itemgetter
from flask_security import login_required
from flask_login import current_user

import pyexcel
import zipfile
import os

from datetime import datetime
from collections import Counter

rk_yd = Blueprint('rk_yd', __name__, template_folder='templates')


#        !!!!  _________________  *** Grupirator ***  _________________  !!!!


# ________________ *** Grupirator words *** ________________ #

@rk_yd.route('grupirator/<folder_id>_<rk_id>')
@login_required
def grupirator(folder_id, rk_id):

    # Выбираем папку с активной рк
    data = Base.objects(id=folder_id).first()
    for q in data['file']:
        if q['id'] == rk_id:
            name_rk = q['name']
            rk_type = q['type']
            mf_id_rk = q['minus_fraze']
            nch = q['nch']

    s = Segment.objects(rk=rk_id)
    # выводим списки минус фраз
    mf = MinusFraze.objects(author=current_user.id)

    return render_template('grupirator.html', name_rk=name_rk, rk_id=rk_id, s=s, data=data, folder_id=folder_id, rk_type=rk_type, id_user=current_user.id, mf=mf, mf_id_rk=mf_id_rk, nch=nch)

# отдаем список минус фраз
@rk_yd.route('/grupirator/up/get_mf_words', methods=['POST'])
@login_required
def get_mf_words():
    data2 = json.loads(request.data.decode('UTF-8'))

    minus_frase=[]
    for mf in MinusFraze.objects(author=current_user.id):
        if data2['id_mf'] == str(mf['id']):
            minus_frase = mf['minus_frase']

    return jsonify({'mf':minus_frase})

# отдаем список сгруппированных фраз
@rk_yd.route('/grupirator/up/get_data_words', methods=['POST'])
@login_required
def get_data_words():
    data2 = json.loads(request.data.decode('UTF-8'))
    id_rk = data2['id_rk']

    s = Segment.objects(rk=id_rk)
    # 1. получаем словарь фраз из активных сегментов
    dict_fraze = {}
    for segment in s:
            dict_fraze.update(segment['words_no'])
            for group in segment.words_yes:
                dict_fraze.update(group[1])

    # ------- Генерируем фразы -----

    #2.Генерируем множество слов из полученных фраз
    list_words = list()
    d_text={}
    for fraze in dict_fraze:
        list_words.extend(fraze.split())
        for word in fraze.split():
            if word in d_text:
                d_text[word].append([fraze,dict_fraze[fraze]])
            else:
                d_text.update({word:[ [fraze,dict_fraze[fraze]] ]})
    count = Counter(list_words)
    set_words = set(list_words)
    list_words = list(set(list_words))

    #3. Получаем список множеств из похожих слов - list_poh
    list_poh=[]
    morph = pymorphy2.MorphAnalyzer()
    for word in list_words:
        if word in set_words:
            morphem_list = get_close_matches(word, set_words, n=10, cutoff = 0.85)
            morphem_set=set(morphem_list)

            morphem_list=list(morphem_set)
            for morphem in morphem_list:
                for i in morph.parse(morphem)[0].lexeme:
                    morphem_set.add(i.methods_stack[0][1])

            list_poh.append(list(filter(lambda mor: mor in set_words, morphem_set)))
            set_words = set_words - morphem_set

    #4. Выводим слова и их кол-во во фразах
    dict_poh_words=[]
    for set_poh in list_poh:
        i=0
        dict_fraze_with_words=[]
        for word_poh in set_poh:
            i += count[word_poh]
            dict_fraze_with_words.extend(d_text[word_poh])
        dict_poh_words.append([set_poh,i,dict_fraze_with_words])
    dict_poh_words = sorted(dict_poh_words, key=itemgetter(1), reverse=True)
    return jsonify({'data':dict_poh_words, 'list_words':list_words })


# ________________ *** Переключение между сегментами *** ________________ #

@rk_yd.route('/grupirator/up/grupirator_view_segment', methods=['POST'])
@login_required
def grupirator_view_segment():
    data2 = json.loads(request.data.decode('UTF-8'))
    list_segment_active = data2['list_segment_active']
    rk_id = data2['id']
    s = Segment.objects(rk=rk_id)

    #1. получаем список фраз из активных сегментов
    dict_fraze = {}
    for id_seg_active in list_segment_active:
        for segment in s:
            if id_seg_active == str(segment.id):
                dict_fraze.update(segment['words_no'])
                words_yes = segment.words_yes.copy()
                for group in words_yes:
                    for words in group[1]:
                        dict_fraze.update(group[1])

    # ------- Генерируем фразы -----

    #2.Генерируем множество слов из полученных фраз
    list_words = list()
    d_text={}
    for fraze in dict_fraze:
        list_words.extend(fraze.split())
        for word in fraze.split():
            if word in d_text:
                d_text[word].append([fraze,dict_fraze[fraze]])
            else:
                d_text.update({word:[ [fraze,dict_fraze[fraze]] ]})
    count = Counter(list_words)
    set_words = set(list_words)
    list_words = list(set(list_words))

    #3. Получаем список множеств из похожих слов - list_poh
    list_poh=[]
    morph = pymorphy2.MorphAnalyzer()
    for word in list_words:
        if word in set_words:
            morphem_list = get_close_matches(word, set_words, n=10, cutoff = 0.85)
            morphem_set=set(morphem_list)

            morphem_list=list(morphem_set)
            for morphem in morphem_list:
                for i in morph.parse(morphem)[0].lexeme:
                    morphem_set.add(i.methods_stack[0][1])

            list_poh.append(list(filter(lambda mor: mor in set_words, morphem_set)))
            set_words = set_words - morphem_set

    #4. Выводим слова и их кол-во во фразах
    dict_poh_words=[]
    for set_poh in list_poh:
        i=0
        dict_fraze_with_words=[]
        for word_poh in set_poh:
            i += count[word_poh]
            dict_fraze_with_words.extend(d_text[word_poh])
        dict_poh_words.append([list(set_poh),i,dict_fraze_with_words])
    dict_poh_words = sorted(dict_poh_words, key=itemgetter(1), reverse=True)
    return jsonify({'data':dict_poh_words, 'list_words':list_words })



# ________________ *** Удаление фраз генератор *** ________________ #

@rk_yd.route('/grupirator/up/grupirator_delete_words', methods=['POST'])
@login_required
def grupirator_delete_words():
    data2 = json.loads(request.data.decode('UTF-8'))
    rk_id = data2['id']
    list_words = data2['arr_words']
    list_segment_active = data2['list_segment_active']
    s = Segment.objects(rk=rk_id)
    active_seg = []
    for seg in s:
        for seg_a in list_segment_active:
            if seg_a == str(seg['id']):
                active_seg.append(seg)

    #Проверяем наличие слова в каждой сгенерированной и несгенерированной фразе
    for seg in active_seg:
        for groupe in seg.words_yes:
            for fraze in list(groupe[1]):
                if bool(set(fraze.split()) & set(list_words)):
                    groupe[1].pop(fraze)
        for groupe in seg.words_yes:
            if len(groupe[1]) == 0:
                seg.words_yes.remove(groupe)
        for fraz_no in list(seg.words_no):
            if bool(set(fraz_no.split()) & set(list_words)):
                seg.words_no.pop(fraz_no)

#Сохраняем сегменты
# подсчет ВЧ/НЧ/Охвата
    nch = data2['nch']
    # заходим в сегменты рк
    for seg in active_seg:
        num_vch=0
        num_nch=0
        ohvat_vch = 0
        ohvat_nch = 0
        words_no = seg.words_no
        words_yes = seg.words_yes
        # заходим список несген фраз
        for i in words_no:
            if int(words_no[i]) >= nch:
                num_vch +=1
                ohvat_vch += int(words_no[i])
            # берем НЧ
            else:
                num_nch +=1
                ohvat_nch += int(words_no[i])
        for groupe in words_yes:
                for word in groupe[1]:
                    if int(groupe[1][word]) >= nch:
                        num_vch +=1
                        ohvat_vch += int(groupe[1][word])
                    # берем НЧ
                    else:
                        num_nch +=1
                        ohvat_nch += int(groupe[1][word])
        seg.num_vch = num_vch
        seg.num_nch = num_nch
        seg.ohvat_vch = ohvat_vch
        seg.ohvat_nch = ohvat_nch
        seg.save()

    return jsonify({})



#______________________ *** Перенос фраз генератор ***______________________#

# ________________ гуляние по папкам
@rk_yd.route('/grupirator/up/grupirator_perenos', methods=['POST'])
@login_required
def grupirator_perenos():
    data2 = json.loads(request.data.decode('UTF-8'))
    data = Base.objects(id=data2['id_folder']).first()
    return jsonify({'data': render_template('/grupirator/grupirator_perenos.html', data=data, folder_id=data2['id_folder'], rk_type=data2['rk_type'])})

# ________________ Отображение сегментов выбранной РК
@rk_yd.route('/grupirator/up/grupirator_perenos_veiw_segment', methods=['POST'])
@login_required
def grupirator_perenos_veiw_segment():
    data2 = json.loads(request.data.decode('UTF-8'))
    s = Segment.objects(rk=data2['id_rk'])
    return jsonify({'data': render_template('/grupirator/grupirator_perenos_veiw_segment.html', s=s)})


# ________________ Сам перенос

@rk_yd.route('/grupirator/up/grupirator_perenos_words', methods=['POST'])
@login_required
def grupirator_perenos_words():
    data2 = json.loads(request.data.decode('UTF-8'))

    # формируем список активных сегментов
    rk_id = data2['rk_id']
    s = Segment.objects(rk=rk_id)
    list_segment_active = data2['list_segment_active']
    active_seg = []
    for seg in s:
        for seg_a in list_segment_active:
            if seg_a == str(seg['id']):
                active_seg.append(seg)

    list_words = data2['arr_words']
    dict_words = {}

    #Проверяем наличие слова в каждой сгенерированной и несгенерированной фразе
    for seg in active_seg:
        for groupe in seg.words_yes:
            for fraze in list(groupe[1]):
                if bool(set(fraze.split()) & set(list_words)):
                    dict_words.update({fraze:groupe[1][fraze]})
                    groupe[1].pop(fraze)
        for groupe in seg.words_yes:
            if len(groupe[1]) == 0:
                seg.words_yes.remove(groupe)
        for fraz_no in list(seg.words_no):
            if bool(set(fraz_no.split()) & set(list_words)):
                dict_words.update({fraz_no:seg.words_no[fraz_no]})
                seg.words_no.pop(fraz_no)
        seg.save()

    data = Base.objects(id=data2['id_folder']).first()
    id_seg = data2['id_seg']
    name_rk = str(data2['name_rk'])
    name_segment = str(data2['name_segment'])

    # 1.переносим в сегмент
    if len(id_seg) > 0:
        seg = Segment.objects(id=id_seg).first()
        for i in dict_words:
            seg['words_no'].update({i:dict_words[i]})
        seg.save()

    # 2.переносим в новый сегмент
    elif len(name_segment) > 0:
        rk_id_kuda = data2['rk_id_kuda']
        name_new_seg = data2['name_segment']
        for i in data.file:
            if i['id'] == rk_id_kuda:
                name_rk_kuda = i['name']
        # Создаем новый сегмент
        seg = Segment(rk=rk_id_kuda, name=data2['name_segment'], words_no=dict_words)
        seg.save()

        # создаем объявления для новых сегментов
        utm_name_rk = name_rk_kuda.replace(' ', '_')
        utm_name_segment = name_new_seg.replace(' ', '_')
        if data2['rk_type'] == 'direct_search':
            yd = YDPoisk(rk=rk_id_kuda, segment=str(seg.id), seg_name=name_new_seg, name_rk=name_rk_kuda)
        else:
            yd = YdRsy(rk=rk_id_kuda, segment=str(seg.id), seg_name=name_new_seg, name_rk=name_rk_kuda)
        yd.utm.update({'utm_campaign':utm_name_rk,'utm_segment':utm_name_segment})
        yd.save()

    # 3.переносим в новую рк
    elif len(name_rk) > 0:
        oid = bson.objectid.ObjectId()
        data.file.append({'name':name_rk, 'type':data2['rk_type'], 'date':datetime.today().strftime('%d.%m.%Y'), 'id':str(oid), 'valuta':"RUB", 'vizitka': '', 'operator': {'Без операторов':False, 'С + у предлогов':True, 'Точное':True}, 'minus_fraze': '', 'nch':25 })
        # сохраняем рк и новый сегмент
        data.save()
        seg = Segment(rk=str(oid), name=name_rk, words_no=dict_words)
        seg.save()

        # создаем объявления для новых сегментов
        utm_name_rk = name_rk.replace(' ', '_')
        if data2['rk_type'] == 'direct_search':
            yd = YDPoisk(rk=str(oid), segment=str(seg.id), seg_name=name_rk, name_rk=name_rk)
        else:
            yd = YdRsy(rk=str(oid), segment=str(seg.id), seg_name=name_rk, name_rk=name_rk)
        yd.utm.update({'utm_campaign':utm_name_rk,'utm_segment':utm_name_rk})
        yd.save()

    # подсчет ВЧ/НЧ/Охвата куда переносили
    if len(data2['rk_id_kuda']) > 0:
        for q in data['file']:
            if q['id'] == data2['rk_id_kuda']:
                nch_kuda = q['nch']
                break
    else:
        nch_kuda = 25

    num_vch=0
    num_nch=0
    ohvat_vch = 0
    ohvat_nch = 0
    words_no = seg.words_no
    words_yes = seg.words_yes
    for i in words_no: # заходим список несген фраз
        if int(words_no[i]) >= nch_kuda:
            num_vch +=1
            ohvat_vch += int(words_no[i])
        else:# берем НЧ
            num_nch +=1
            ohvat_nch += int(words_no[i])
    for groupe in words_yes:
            for word in groupe[1]:
                if int(groupe[1][word]) >= nch_kuda:
                    num_vch +=1
                    ohvat_vch += int(groupe[1][word])
                else:# берем НЧ
                    num_nch +=1
                    ohvat_nch += int(groupe[1][word])
    seg.num_vch = num_vch
    seg.num_nch = num_nch
    seg.ohvat_vch = ohvat_vch
    seg.ohvat_nch = ohvat_nch
    seg.save()

# подсчет ВЧ/НЧ/Охвата откуда переносили
    nch_otkuda = int(data2['chastota'])
    for seg in active_seg: # заходим в сегменты рк
        num_vch=0
        num_nch=0
        ohvat_vch = 0
        ohvat_nch = 0
        words_no = seg.words_no
        words_yes = seg.words_yes
        for i in words_no: # заходим список несген фраз
            if int(words_no[i]) >= nch_otkuda:
                num_vch +=1
                ohvat_vch += int(words_no[i])
            else:# берем НЧ
                num_nch +=1
                ohvat_nch += int(words_no[i])
        for groupe in words_yes:
                for word in groupe[1]:
                    if int(groupe[1][word]) >= nch_otkuda:
                        num_vch +=1
                        ohvat_vch += int(groupe[1][word])
                    else:# берем НЧ
                        num_nch +=1
                        ohvat_nch += int(groupe[1][word])
        seg.num_vch = num_vch
        seg.num_nch = num_nch
        seg.ohvat_vch = ohvat_vch
        seg.ohvat_nch = ohvat_nch
        seg.save()

    return jsonify({})



#              ________________ POISK ________________

@rk_yd.route('/grupirator/up/grupirator_poisk', methods=['POST'])
@login_required
def grupirator_poisk():
    data2 = json.loads(request.data.decode('UTF-8'))
    id = data2['id']
    list_segment_active = data2['list_segment_active']
    text = data2['text']
    s = Segment.objects(rk=id)

    # получаем список фраз из активных сегментов содержащие нашу фразу
    dict_fraze = {}
    for id_seg_active in list_segment_active:
        for segment in s:
            if id_seg_active == str(segment.id):
                for word in segment['words_no']:
                    if text in word:
                        dict_fraze.update({word:segment['words_no'][word]})
                for group in segment['words_yes']:
                    for words in group[1]:
                        if text in words:
                            dict_fraze.update(group[1])

    # ------- Генерируем фразы -----

    #2.Генерируем множество слов из полученных фраз
    list_words = list()
    d_text={}
    for fraze in dict_fraze:
        list_words.extend(fraze.split())
        for word in fraze.split():
            if word in d_text:
                d_text[word].append([fraze,dict_fraze[fraze]])
            else:
                d_text.update({word:[ [fraze,dict_fraze[fraze]] ]})
    count = Counter(list_words)
    set_words = set(list_words)
    list_words = list(set(list_words))

    #3. Получаем список множеств из похожих слов - list_poh
    list_poh=[]
    morph = pymorphy2.MorphAnalyzer()
    for word in list_words:
        if word in set_words:
            morphem_list = get_close_matches(word, set_words, n=10, cutoff = 0.85)
            morphem_set=set(morphem_list)

            morphem_list=list(morphem_set)
            for morphem in morphem_list:
                for i in morph.parse(morphem)[0].lexeme:
                    morphem_set.add(i.methods_stack[0][1])

            list_poh.append(list(filter(lambda mor: mor in set_words, morphem_set)))
            set_words = set_words - morphem_set

    #4. Выводим слова и их кол-во во фразах
    dict_poh_words=[]
    for set_poh in list_poh:
        i=0
        dict_fraze_with_words=[]
        for word_poh in set_poh:
            i += count[word_poh]
            dict_fraze_with_words.extend(d_text[word_poh])
        dict_poh_words.append([list(set_poh),i,dict_fraze_with_words])
    dict_poh_words = sorted(dict_poh_words, key=itemgetter(1), reverse=True)
    return jsonify({'data':dict_poh_words })


#______________________ *** Минус фразы ***______________________#

# ________________ создание и добавление в список слов
@rk_yd.route('/grupirator/up/create_minus_frase', methods=['POST'])
@login_required
def create_minus_frase():
    data2 = json.loads(request.data.decode('UTF-8'))
    mf=MinusFraze(author=current_user.id, name=data2['name'], minus_frase=list(set(data2['words_list'])))
    mf.save()
    minus_frase = mf.minus_frase

    data = Base.objects(author=current_user.id)
    for folder in data:
        for rk in folder['file']:
            if data2['id_rk'] == rk['id']:
                rk.update({'minus_fraze':mf.id})
                folder.save()

    return jsonify({'mf': '<option name="name_mf" data-id="'+str(mf.id)+'">'+mf.name+'</option>', 'data': minus_frase, 'id_mf':str(mf.id)})

# ________________ добавление в текущий список слов
@rk_yd.route('/grupirator/up/add_words_mf', methods=['POST'])
@login_required
def add_words_mf():
    data2 = json.loads(request.data.decode('UTF-8'))

    mf = MinusFraze.objects(id=data2['id_mf']).first()
    mf['minus_frase'].extend(data2['words_list'])
    mf['minus_frase'] = list(set(mf['minus_frase']))
    mf.save()

    return jsonify({'data': mf})


# ________________ удаление минус фраз

# удаление списка
@rk_yd.route('/grupirator/up/del_mf', methods=['POST'])
@login_required
def del_mf():
    data2 = json.loads(request.data.decode('UTF-8'))

    mf = MinusFraze.objects(id=data2['id_mf']).first()
    mf.delete()

    data = Base.objects(id=data2['id_folder']).first()
    for rk in data['file']:
        if data2['id_rk'] == rk['id']:
            rk.pop('minus_fraze')
            rk.update({'minus_fraze':''})
            data.save()

    return jsonify({})

# открепление списка от рк
@rk_yd.route('/grupirator/up/del_minus_frase', methods=['POST'])
@login_required
def del_minus_frase():
    data2 = json.loads(request.data.decode('UTF-8'))
    data = Base.objects(id=data2['id_folder']).first()
    for rk in data['file']:
        if data2['id_rk'] == rk['id']:
            rk.pop('minus_fraze')
            rk.update({'minus_fraze':''})
            data.save()

    return jsonify({})


# ________________ сохранение списка минус фраз
@rk_yd.route('/grupirator/up/save_mf', methods=['POST'])
@login_required
def save_mf():
    data2 = json.loads(request.data.decode('UTF-8'))

# сохранение списка минус фраз
    mf=MinusFraze.objects(id=data2['id_mf']).first()
    mf.minus_frase = data2['mf_list']
    mf.save()

# добавление списка в рк
    data = Base.objects(id=data2['folder_id']).first()
    for rk in data['file']:
        if data2['id_rk'] == rk['id']:
            rk.update({'minus_fraze':mf.id})
            data.save()

    return jsonify({})



#______________________ *** Скачивание файлов ***______________________#


# ________________ готовую рк ПОИСК
@rk_yd.route('/download_rk/<id_folder>/<id_rk>')
@login_required
def download_rk(id_folder,id_rk):
    # получаем данные РК
    data = Base.objects(id=id_folder).first()
    for rk in data['file']:
        if id_rk == rk['id']:
            name_rk = rk['name']
            vizitka = rk['vizitka']
            valuta = rk['valuta']
            operator = rk['operator']
            minus_fraze = rk['minus_fraze']

    book = pyexcel.get_book(file_name="base.xlsx")

    # валюта
    book['Тексты'][7,7] = valuta

    # минус-фразы
    if minus_fraze != '':
        mf = MinusFraze.objects(id=minus_fraze).first()
        mfstr=''
        minus_frase = mf.minus_frase
        for i in minus_frase:
            mfstr+='-'+str(i)+' '
            book['Тексты'][8,4] = mfstr[:-1]

    strok=['-', 'Текстово-графическое', '-', '', '', '', '-', '', '', '', '', '', '', 35, 30, 85, '', '', '', '', '', '-', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    strok2=['+', 'Текстово-графическое', '-', '', '', '', '-', '', '', '', '', '', '', 35, 30, 85, '', '', '', '', '', '-', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

    # визитка
    if vizitka != '':
        viz = Vizitka.objects(id = vizitka).first()
        if viz != None:
            viz = Vizitka.objects(id = vizitka).first()
            book['Контактная информация'][8,2] = viz['country']
            book['Контактная информация'][10,2] = viz['sity']
            book['Контактная информация'][12,2] = viz['tel'][0]
            book['Контактная информация'][12,3] = viz['tel'][1]
            book['Контактная информация'][12,4] = viz['tel'][2]
            book['Контактная информация'][16,1] = viz['company']
            book['Контактная информация'][19,1] = viz['contact']
            book['Контактная информация'][22,1] = viz['street']
            book['Контактная информация'][22,3] = viz['house']
            book['Контактная информация'][22,4] = viz['corp']
            book['Контактная информация'][22,5] = viz['ofice']
            book['Контактная информация'][26,1] = viz['week1']
            book['Контактная информация'][26,2] = viz['week2']
            book['Контактная информация'][26,4] = viz['chas1']+':'+viz['minute1']
            book['Контактная информация'][26,5] = viz['chas2']+':'+viz['minute2']
            book['Контактная информация'][12,8] = viz['ogrn']
            book['Контактная информация'][16,8] = viz['email']
            book['Контактная информация'][22,8] = viz['podrobnee']

            strok[21]='+'
            strok2[21]='+'

    s = Segment.objects(rk=id_rk)
    n=0
    rk=1
    list_rk=[]
    for seg in s:
        seg_id = str(seg.id)
        words_yes = seg.words_yes.copy()
        # берем объявление сегмента
        yd1 = YDPoisk.objects(segment=seg_id, num=1).first()
        # Формируем 1-е объявление
        if yd1.mobil == True:
            strok[2] = '+'
        else:
            strok[2] = '-'
        strok[12] = yd1.text
        new_utm=''
        for utm in yd1.new_utm:
            new_utm += utm+'='+yd1.new_utm[utm]+'&'
        if len(new_utm)>1:
            new_utm = '&'+new_utm
            new_utm = new_utm[:-1]
        else:
            new_utm=''
        utm = 'utm_source='+yd1.utm['utm_source']+'&'+'utm_campaign='+yd1.utm['utm_campaign']+'&'+'utm_segment='+yd1.utm['utm_segment']+'&'+'utm_content='+yd1.utm['utm_content']+'&'+'utm_term='+yd1.utm['utm_term']
        # проверка на наличие якоря в ссылке
        yakor=yd1.url.split('#')
        if len(yakor) == 2:
            strok[16] = yakor[0]+'?'+utm+new_utm+'#'+yakor[1]
        else:
            strok[16] = yd1.url+'?'+utm+new_utm
        strok[17] = yd1.url_word
        # быстрые ссылки
        url_bs = []
        for url in yd1.bs:
            yakor=url[1].split('#')
            if len(yakor) == 2:
                yakor[1] = '#'+yakor[1]
                url_bs.append(yakor)
            else:
                yakor.append('')
                url_bs.append(yakor)
        n_bs = 0
        for i in yd1.bs:
            if len(i[0]) >0:
                n_bs+=1
        if n_bs == 4:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]+'||'+yd1.bs[2][0]+'||'+yd1.bs[3][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]+'||'+yd1.bs[2][2]+'||'+yd1.bs[3][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]+'||'+url_bs[3][0]+'?'+utm+new_utm+url_bs[3][1]
        elif n_bs == 3:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]+'||'+yd1.bs[2][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]+'||'+yd1.bs[2][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]
        elif n_bs == 2:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]
        elif n_bs == 1:
            strok[24] = yd1.bs[0][0]
            strok[25] = yd1.bs[0][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]
        elif n_bs == 0:
            strok[24] = ''
            strok[25] = ''
            strok[26] = ''
        # изображение
        if yd1.img == '':
            strok[30] = ''
        else:
            strok[30] = 'https://shinta.ru/static/uploads/'+yd1.img
        # уточнения
        n_utoch = 0
        for i in yd1.utoch:
            if len(i) >0:
                n_utoch+=1
        if n_utoch == 4:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]+'||'+yd1.utoch[2]+'||'+yd1.utoch[3]
        elif n_utoch == 3:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]+'||'+yd1.utoch[2]
        elif n_utoch == 2:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]
        elif n_utoch == 1:
            strok[33] = yd1.utoch[0]
        elif n_utoch == 0:
            strok[33] = ''
        # проверяем наличие 2-х заголовоков различной длинны
        yd1_zag21 = yd1.zagolovok2[0]
        yd1_zag22 = ''
        yd1_zag23 = ''
        yd1_zag24 = ''
        if len(yd1.zagolovok2[1])>0:
            yd1_zag22 = yd1.zagolovok2[1]
        if len(yd1.zagolovok2[2])>0:
            yd1_zag23 = yd1.zagolovok2[2]
        if len(yd1.zagolovok2[3])>0:
            yd1_zag24 = yd1.zagolovok2[3]
        # Формируем 2-е объявление
        yd = YDPoisk.objects(segment=seg_id)
        if len(yd) >1:
            list_strok2 = []
            list_zag2 = []
            for ob in yd:
                if ob.num >1:
                    if ob.mobil == True:
                        strok2[2] = '+'
                    else:
                        strok2[2] = '-'
                    strok2[12] = ob.text
                    new_utm=''
                    for utm in ob.new_utm:
                        new_utm += utm+'='+ob.new_utm[utm]+'&'
                    if len(new_utm)>1:
                        new_utm = '&'+new_utm
                        new_utm = new_utm[:-1]
                    else:
                        new_utm=''
                    utm = 'utm_source='+ob.utm['utm_source']+'&'+'utm_campaign='+ob.utm['utm_campaign']+'&'+'utm_segment='+ob.utm['utm_segment']+'&'+'utm_content='+ob.utm['utm_content']+'&'+'utm_term='+ob.utm['utm_term']
                    # проверка на наличие якоря в ссылке
                    yakor=ob.url.split('#')
                    if len(yakor) == 2:
                        strok2[16] = yakor[0]+'?'+utm+new_utm+'#'+yakor[1]
                    else:
                        strok2[16] = ob.url+'?'+utm+new_utm
                    strok2[17] = ob.url_word
                    # быстрые ссылки
                    url_bs = []
                    for url in ob.bs:
                        yakor=url[1].split('#')
                        if len(yakor) == 2:
                            yakor[1] = '#'+yakor[1]
                            url_bs.append(yakor)
                        else:
                            yakor.append('')
                            url_bs.append(yakor)
                    n_bs = 0
                    for i in ob.bs:
                        if len(i[0]) >0:
                            n_bs+=1
                    if n_bs == 4:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]+'||'+ob.bs[2][0]+'||'+ob.bs[3][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]+'||'+ob.bs[2][2]+'||'+ob.bs[3][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]+'||'+url_bs[3][0]+'?'+utm+new_utm+url_bs[3][1]
                    elif n_bs == 3:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]+'||'+ob.bs[2][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]+'||'+ob.bs[2][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]
                    elif n_bs == 2:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]
                    elif n_bs == 1:
                        strok2[24] = ob.bs[0][0]
                        strok2[25] = ob.bs[0][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]
                    elif n_bs == 0:
                        strok2[24] = ''
                        strok2[25] = ''
                        strok2[26] = ''
                    # изображение
                    if ob.img == '':
                        strok2[30] = ''
                    else:
                        strok2[30] = 'https://shinta.ru/static/uploads/'+ob.img
                    # уточнения
                    n_utoch = 0
                    for i in ob.utoch:
                        if len(i) >0:
                            n_utoch+=1
                    if n_utoch == 4:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]+'||'+ob.utoch[2]+'||'+ob.utoch[3]
                    elif n_utoch == 3:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]+'||'+ob.utoch[2]
                    elif n_utoch == 2:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]
                    elif n_utoch == 1:
                        strok2[33] = ob.utoch[0]
                    elif n_utoch == 0:
                        strok2[33] = ''
                    # проверяем наличие 2-х заголовоков различной длинны
                    yd_zag21 = ob.zagolovok2[0]
                    yd_zag22 = ''
                    yd_zag23 = ''
                    yd_zag24 = ''
                    if len(ob.zagolovok2[1])>0:
                        yd_zag22 = ob.zagolovok2[1]
                    if len(ob.zagolovok2[2])>0:
                        yd1_zag23 = ob.zagolovok2[2]
                    if len(ob.zagolovok2[3])>0:
                        yd_zag24 = ob.zagolovok2[3]
                    strok2_n=strok2.copy()
                    list_strok2.append(strok2_n)
                    list_zag2.append([yd_zag21,yd_zag22,yd_zag23,yd_zag24])
        #заходим в группы
        for gp in words_yes:
            strok_n=strok.copy()
            n+=1
            if n == 1001:
                if rk == 1:
                    save_name_rk = name_rk.replace(' ', '_')
                    output_zip=zipfile.ZipFile(save_name_rk+'.zip','w')
                book['Тексты'].row += list_rk
                book.save_as(name_rk+str(rk)+".xlsx")
                output_zip.write(name_rk+str(rk)+".xlsx")
                os.remove(name_rk+str(rk)+".xlsx")

                l=list(range(11, 200001))
                book['Тексты'].delete_rows(row_indices=l)

                n=1
                rk+=1
                list_rk=[]
            strok_n[5] = n
            strok_n[4] = gp[0]
            strok_n[10] = gp[2]
            strok_n[11]= yd1_zag21
            # есл НЧ то просто добавляем фразу
            if len(gp[1]) > 1:
                for word in gp[1]:
                    strok_nch = strok_n.copy()
                    strok_nch[8] = word
                    list_rk.append(strok_nch)
                # вторые объявления НЧ
                if len(yd) >1:
                    for strok2 in list_strok2:
                        strok2[4] = gp[0]
                        strok2[10] = gp[2]
                        strok2[11]= yd_zag21
                        # 2.Номер группы
                        strok2[5] = n
                        strok2_n = strok2.copy()
                        list_rk.append(strok2_n)
            # Если ВЧ то
            else:
                for word in gp[1]:
                    if 32 > len(word) >= 28 and len(yd1_zag22)>0:
                        strok_n[11]= yd1_zag22
                    elif 28 > len(word) >= 24 and len(yd1_zag23)>0:
                        strok_n[11]= yd1_zag23
                    elif len(word) < 24 and len(yd1_zag24)>0:
                        strok_n[11]= yd1_zag24
                    if operator['Без операторов'] == True:
                        strok_bez = strok_n.copy()
                        strok_bez[8] = word
                        list_rk.append(strok_bez)
                    if operator['С + у предлогов'] == True:
                        strok_plus = strok_n.copy()
                        #Формируем новый список с целью проверки предлогов, и задаем список для проверки
                        q = word.split()
                        p = ['и', 'на', 'в']
                        #Если последнее слово содержится в списоке, то добавляем + к нему
                        num=-1
                        for i in q:
                            num+=1
                            for z in p:
                                if i == z:
                                    q[num]='+'+i
                        strok_plus[8]=' '.join(q)
                        list_rk.append(strok_plus)
                    if operator['Точное'] == True:
                        strok_toch = strok_n.copy()
                        strok_toch[8] = '"'+word+'"'
                        list_rk.append(strok_toch)
                    # вторые объявления
                    if len(yd) >1:
                        num_zag=-1
                        for strok2 in list_strok2:
                            num_zag+=1
                            strok2[4] = gp[0]
                            strok2[10] = gp[2]
                            strok2[5] = n
                            strok2[11] = list_zag2[num_zag][0]
                            if 32 > len(word) >= 28 and len(list_zag2[num_zag][1])>0:
                                strok2[11]= list_zag2[num_zag][1]
                            elif 28 > len(word) >= 24 and len(list_zag2[num_zag][2])>0:
                                strok2[11]= list_zag2[num_zag][2]
                            elif len(word) < 24 and len(list_zag2[num_zag][3])>0:
                                strok2[11]= list_zag2[num_zag][3]
                            strok2_n=strok2.copy()
                            list_rk.append(strok2_n)


    # объявления
    book['Тексты'].row += list_rk
    save_name_rk = name_rk.replace(' ', '_')
    if rk > 1:
        book.save_as(save_name_rk+str(rk)+".xlsx")
        output_zip.write(save_name_rk+str(rk)+".xlsx")
        output_zip.close()
        os.remove(save_name_rk+str(rk)+".xlsx")
        return send_file('/root/shinta/'+save_name_rk+'.zip', as_attachment=True), os.remove(save_name_rk+'.zip')
    else:
        book.save_as(save_name_rk+".xlsx")
        return send_file('/root/shinta/'+save_name_rk+'.xlsx', as_attachment=True), os.remove(save_name_rk+".xlsx")


# ________________ готовую рк РСЯ
@rk_yd.route('/download_rk_rsy/<id_folder>/<id_rk>')
@login_required
def download_rk_rsy(id_folder,id_rk):
    # получаем данные РК
    data = Base.objects(id=id_folder).first()
    for rk in data['file']:
        if id_rk == rk['id']:
            name_rk = rk['name']
            vizitka = rk['vizitka']
            valuta = rk['valuta']
            minus_fraze = rk['minus_fraze']

    book = pyexcel.get_book(file_name="base.xlsx")

    # валюта
    book['Тексты'][7,7] = valuta

    # минус-фразы
    if minus_fraze != '':
        mf = MinusFraze.objects(id=minus_fraze).first()
        mfstr=''
        minus_frase = mf.minus_frase
        for i in minus_frase:
            mfstr+='-'+str(i)+' '
            book['Тексты'][8,4] = mfstr[:-1]

    # визитка
    strok=['-', 'Текстово-графическое', '-', '', '', '', '-', '', '', '', '', '', '', 35, 30, 85, '', '', '', '', '', '-', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    strok2=['+', 'Текстово-графическое', '-', '', '', '', '-', '', '', '', '', '', '', 35, 30, 85, '', '', '', '', '', '-', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']

    if vizitka != '':
        viz = Vizitka.objects(id = vizitka).first()
        if viz != None :
            book['Контактная информация'][8,2] = viz['country']
            book['Контактная информация'][10,2] = viz['sity']
            book['Контактная информация'][12,2] = viz['tel'][0]
            book['Контактная информация'][12,3] = viz['tel'][1]
            book['Контактная информация'][12,4] = viz['tel'][2]
            book['Контактная информация'][16,1] = viz['company']
            book['Контактная информация'][19,1] = viz['contact']
            book['Контактная информация'][22,1] = viz['street']
            book['Контактная информация'][22,3] = viz['house']
            book['Контактная информация'][22,4] = viz['corp']
            book['Контактная информация'][22,5] = viz['ofice']
            book['Контактная информация'][26,1] = viz['week1']
            book['Контактная информация'][26,2] = viz['week2']
            book['Контактная информация'][26,4] = viz['chas1']+':'+viz['minute1']
            book['Контактная информация'][26,5] = viz['chas2']+':'+viz['minute2']
            book['Контактная информация'][12,8] = viz['ogrn']
            book['Контактная информация'][16,8] = viz['email']
            book['Контактная информация'][22,8] = viz['podrobnee']

            strok[21]='+'
            strok2[21]='+'

    s = Segment.objects(rk=id_rk)
    n=0
    rk=1
    list_rk=[]
    for seg in s:
        seg_id = str(seg.id)
        words_yes = seg.words_yes.copy()
        # берем объявление сегмента
        yd1 = YdRsy.objects(segment=seg_id, num=1).first()
        # Формируем 1-е объявление
        if yd1.mobil == True:
            strok[2] = '+'
        else:
            strok[2] = '-'
        strok[12] = yd1.text
        new_utm=''
        for utm in yd1.new_utm:
            new_utm += utm+'='+yd1.new_utm[utm]+'&'
        if len(new_utm)>1:
            new_utm = '&'+new_utm
            new_utm = new_utm[:-1]
        else:
            new_utm=''
        utm = 'utm_source='+yd1.utm['utm_source']+'&'+'utm_campaign='+yd1.utm['utm_campaign']+'&'+'utm_segment='+yd1.utm['utm_segment']+'&'+'utm_content='+yd1.utm['utm_content']+'&'+'utm_term='+yd1.utm['utm_term']
        # проверка на наличие якоря в ссылке
        yakor=yd1.url.split('#')
        if len(yakor) == 2:
            strok[16] = yakor[0]+'?'+utm+new_utm+'#'+yakor[1]
        else:
            strok[16] = yd1.url+'?'+utm+new_utm
        strok[17] = yd1.url_word
        # быстрые ссылки
        url_bs = []
        for url in yd1.bs:
            yakor=url[1].split('#')
            if len(yakor) == 2:
                yakor[1] = '#'+yakor[1]
                url_bs.append(yakor)
            else:
                yakor.append('')
                url_bs.append(yakor)
        n_bs = 0
        for i in yd1.bs:
            if len(i[0]) >0:
                n_bs+=1
        if n_bs == 4:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]+'||'+yd1.bs[2][0]+'||'+yd1.bs[3][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]+'||'+yd1.bs[2][2]+'||'+yd1.bs[3][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]+'||'+url_bs[3][0]+'?'+utm+new_utm+url_bs[3][1]
        elif n_bs == 3:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]+'||'+yd1.bs[2][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]+'||'+yd1.bs[2][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]
        elif n_bs == 2:
            strok[24] = yd1.bs[0][0]+'||'+yd1.bs[1][0]
            strok[25] = yd1.bs[0][2]+'||'+yd1.bs[1][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]
        elif n_bs == 1:
            strok[24] = yd1.bs[0][0]
            strok[25] = yd1.bs[0][2]
            strok[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]
        elif n_bs == 0:
            strok[24] = ''
            strok[25] = ''
            strok[26] = ''
        # изображение
        if yd1.img == '':
            strok[30] = ''
        else:
            strok[30] = 'https://shinta.ru/static/uploads/'+yd1.img
        # уточнения
        n_utoch = 0
        for i in yd1.utoch:
            if len(i) >0:
                n_utoch+=1
        if n_utoch == 4:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]+'||'+yd1.utoch[2]+'||'+yd1.utoch[3]
        elif n_utoch == 3:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]+'||'+yd1.utoch[2]
        elif n_utoch == 2:
            strok[33] = yd1.utoch[0]+'||'+yd1.utoch[1]
        elif n_utoch == 1:
            strok[33] = yd1.utoch[0]
        elif n_utoch == 0:
            strok[33] = ''
        # берем заголовоки
        yd1_zag1 = yd1.zagolovok[0]
        yd1_zag2 = yd1.zagolovok[1]
        # Формируем 2-е объявление
        yd = YdRsy.objects(segment=seg_id)
        if len(yd) >1:
            list_strok2 = []
            list_zag = []
            for ob in yd:
                if ob.num >1:
                    if ob.mobil == True:
                        strok2[2] = '+'
                    else:
                        strok2[2] = '-'
                    strok2[12] = ob.text
                    new_utm=''
                    for utm in ob.new_utm:
                        new_utm += utm+'='+ob.new_utm[utm]+'&'
                    if len(new_utm)>1:
                        new_utm = '&'+new_utm
                        new_utm = new_utm[:-1]
                    else:
                        new_utm=''
                    utm = 'utm_source='+ob.utm['utm_source']+'&'+'utm_campaign='+ob.utm['utm_campaign']+'&'+'utm_segment='+ob.utm['utm_segment']+'&'+'utm_content='+ob.utm['utm_content']+'&'+'utm_term='+ob.utm['utm_term']
                    # проверка на наличие якоря в ссылке
                    yakor=ob.url.split('#')
                    if len(yakor) == 2:
                        strok2[16] = yakor[0]+'?'+utm+new_utm+'#'+yakor[1]
                    else:
                        strok2[16] = ob.url+'?'+utm+new_utm
                    strok2[17] = ob.url_word
                    # быстрые ссылки
                    url_bs = []
                    for url in ob.bs:
                        yakor=url[1].split('#')
                        if len(yakor) == 2:
                            yakor[1] = '#'+yakor[1]
                            url_bs.append(yakor)
                        else:
                            yakor.append('')
                            url_bs.append(yakor)
                    n_bs = 0
                    for i in ob.bs:
                        if len(i[0]) >0:
                            n_bs+=1
                    if n_bs == 4:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]+'||'+ob.bs[2][0]+'||'+ob.bs[3][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]+'||'+ob.bs[2][2]+'||'+ob.bs[3][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]+'||'+url_bs[3][0]+'?'+utm+new_utm+url_bs[3][1]
                    elif n_bs == 3:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]+'||'+ob.bs[2][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]+'||'+ob.bs[2][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]+'||'+url_bs[2][0]+'?'+utm+new_utm+url_bs[2][1]
                    elif n_bs == 2:
                        strok2[24] = ob.bs[0][0]+'||'+ob.bs[1][0]
                        strok2[25] = ob.bs[0][2]+'||'+ob.bs[1][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]+'||'+url_bs[1][0]+'?'+utm+new_utm+url_bs[1][1]
                    elif n_bs == 1:
                        strok2[24] = ob.bs[0][0]
                        strok2[25] = ob.bs[0][2]
                        strok2[26] = url_bs[0][0]+'?'+utm+new_utm+url_bs[0][1]
                    elif n_bs == 0:
                        strok2[24] = ''
                        strok2[25] = ''
                        strok2[26] = ''
                    # изображение
                    if ob.img == '':
                        strok2[30] = ''
                    else:
                        strok2[30] = 'https://shinta.ru/static/uploads/'+ob.img
                    # уточнения
                    n_utoch = 0
                    for i in ob.utoch:
                        if len(i) >0:
                            n_utoch+=1
                    if n_utoch == 4:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]+'||'+ob.utoch[2]+'||'+ob.utoch[3]
                    elif n_utoch == 3:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]+'||'+ob.utoch[2]
                    elif n_utoch == 2:
                        strok2[33] = ob.utoch[0]+'||'+ob.utoch[1]
                    elif n_utoch == 1:
                        strok2[33] = ob.utoch[0]
                    elif n_utoch == 0:
                        strok2[33] = ''
                    strok2_n=strok2.copy()
                    list_strok2.append(strok2_n)
                    # берем заголовки
                    list_zag.append([yd1.zagolovok[0],yd1.zagolovok[1]])
        #заходим в группы
        for gp in words_yes:
            strok_n=strok.copy()
            n+=1
            if n == 1001:
                if rk == 1:
                    output_zip=zipfile.ZipFile(name_rk+'.zip','w')
                book['Тексты'].row += list_rk
                book.save_as(name_rk+str(rk)+".xlsx")
                output_zip.write(name_rk+str(rk)+".xlsx")
                os.remove(name_rk+str(rk)+".xlsx")

                l=list(range(11, 200001))
                book['Тексты'].delete_rows(row_indices=l)

                n=1
                rk+=1
                list_rk=[]
            strok_n[5] = n
            strok_n[4] = gp[0]
            strok_n[10] = yd1_zag1
            strok_n[11]= yd1_zag2
            # есл НЧ то просто добавляем фразу
            for word in gp[1]:
                strok_nch = strok_n.copy()
                strok_nch[8] = word
                list_rk.append(strok_nch)
            # вторые объявления НЧ
            if len(yd) >1:
                num_zag=-1
                for strok2 in list_strok2:
                    num_zag+=1
                    strok2[4] = gp[0]
                    strok2[10] = list_zag[num_zag][0]
                    strok2[11]= list_zag[num_zag][1]
                    # 2.Номер группы
                    strok2[5] = n
                    strok2_n = strok2.copy()
                    list_rk.append(strok2_n)
    # объявления
    book['Тексты'].row += list_rk
    save_name_rk = name_rk.replace(' ', '_')
    if rk > 1:
        book.save_as(save_name_rk+str(rk)+".xlsx")
        output_zip.write(save_name_rk+str(rk)+".xlsx")
        output_zip.close()
        os.remove(save_name_rk+str(rk)+".xlsx")
        return send_file('/root/shinta/'+save_name_rk+'.zip', as_attachment=True), os.remove(save_name_rk+'.zip')
    else:
        book.save_as(save_name_rk+".xlsx")
        return send_file('/root/shinta/'+save_name_rk+'.xlsx', as_attachment=True), os.remove(save_name_rk+".xlsx")


# ________________ структуру рк
@rk_yd.route('/download_structure2/<id_folder>/<id_rk>')
@login_required
def download_structure2(id_folder,id_rk):
    # получаем данные РК
    data = Base.objects(id=id_folder).first()
    for rk in data['file']:
        if id_rk == rk['id']:
            name_rk = rk['name']
            mf_rk = str(rk['minus_fraze'])

    s = Segment.objects(rk=id_rk)

    book = pyexcel.get_book(file_name="structure.xlsx")
    for seg in s:
        extra_data = [ ["Сегмент", "Запрос", "Частота", ""] ]
        words_no = seg.words_no.copy()
        for word in words_no:
            extra_data.append([seg.name,word,words_no[word]])
        words_yes = seg.words_yes.copy()
        for gp in words_yes:
            for word in gp[1]:
                extra_data.append([seg.name,word,gp[1][word]])
        sheet2 = pyexcel.Sheet(extra_data)
        book['Структура'].column += sheet2

    if len(mf_rk) > 0 :
        list_seg=[]
        mf = MinusFraze.objects(id=mf_rk).first()
        for m_word in mf.minus_frase:
            list_seg.append([m_word])
        book['Минус-фразы'].row += list_seg
    book.save_as(name_rk+".xls")
    return send_file('/root/shinta/'+name_rk+'.xls', as_attachment=True), os.remove(name_rk+".xls")


# ________________перенос в ads
@rk_yd.route('/up/perenos_ads', methods=['POST'])
@login_required
def perenos_ads():
    data2 = json.loads(request.data.decode('UTF-8'))
    id_rk = data2['id_rk']
    id_folder = data2['id_folder']
    name_rk = data2['name_rk']
    nch = data2['nch']

    # 1. Копируем запись в Base о новой рк и ее данные
    data = Base.objects(id=id_folder).first()
    for rk in data.file:
        if id_rk == rk['id']:
            id_rk_new = bson.objectid.ObjectId()
            minus_fraze = rk['minus_fraze']
            data.file.append({'name':name_rk, 'type':'ads_search', 'date':datetime.today().strftime('%d.%m.%Y'), 'id':str(id_rk_new), 'lang': {'Русский':True, 'Английский':True}, 'balance': 0, 'operator': {'Широкое':False, 'Широкое с модификатором':True, 'Фразовое':False, 'Точное':True}, 'minus_fraze': minus_fraze, 'nch':nch  })
            data.save()

    # 2. Копируем сегменты в SegAds
    s= Segment.objects(rk=id_rk)
    for seg in s:
        id_seg_new = bson.objectid.ObjectId()
        name_seg = seg['name']
        # делаем заголовки
        words_yes = seg['words_yes'].copy()
        n=-1
        for zag in words_yes:
            n+=1
            zag2 = ''
            for word in zag[2].split():
                if len(zag2+word)<=30:
                    zag2 +=word +' '
                else:
                    break
            #Формируем новый список с целью проверки последнего слова, и задаем список для проверки
            q = zag2.split()
            p = ['чем', 'в', 'без', 'до', 'из', 'к', 'на', 'по', 'о', 'от', 'перед', 'при', 'через', 'с', 'у', 'за', 'над', 'об', 'под', 'про', 'для', 'как']

            #Если последнее слово содержится в исключаемом списоке, то выводим строку без него, иначе выводим всю строку
            if len(q) > 0:
                if q[-1] in p:
                    zag2=' '.join(q[:-1])
            else:
                zag2=''
            words_yes[n][2] = zag2.rstrip().replace('!', '.')
        SegAds(id=id_seg_new, rk=str(id_rk_new), name=name_seg, words_yes=words_yes.copy(),words_no=seg['words_no'].copy(),num_vch=seg['num_vch'],num_nch=seg['num_nch'],ohvat_vch=seg['ohvat_vch'],ohvat_nch=seg['ohvat_nch'], cena= '0' ).save()

        # 3. Копируем объявления в AdsPoisk
        yd_list= YDPoisk.objects(segment=str(seg['id']))
        for yd in yd_list:
            # заголовки
            zag2_list = yd['zagolovok2']
            zag2 = not_simbol_ads(yd['zagolovok2'][0])
            zag2_list.remove(zag2)
            zag3=''
            for zag in zag2_list:
                if zag != '' and len(zag) <=30:
                    zag3 = zag
            # быстрые ссылки
            bs_list = yd['bs'].copy()
            n=-1
            for bs in bs_list:
                n+=1
                text_bs = ''
                # копируем заголовки
                for word in bs[0].split():
                    if len(text_bs+word)<=25:
                        text_bs += word +' '
                    else:
                        break
                bs_list[n][0] = not_simbol_ads(text_bs.rstrip())
                # разбиваем описание на 2
                text_opis1 = ''
                text_opis2 = ''
                control_opis = 0
                for word in bs[2].split():
                    if len(text_opis1+word)<=35 and control_opis == 0:
                        text_opis1 += word +' '
                    else:
                        control_opis += 1
                        text_opis2 += word +' '
                if len(text_opis2) == 0:
                    l = len(text_opis1) + 1
                    part_1 = text_opis1[0:l//2]
                    part_2 = text_opis1[l//2:]
                    text_opis1 = part_1
                    text_opis2 = not_simbol_ads(part_2)
                bs_list[n][2] = not_simbol_ads(text_opis1.rstrip())
                bs_list[n].append( not_simbol_ads(text_opis2.rstrip()) )
            # урлы отображ
            url_word_old=yd['url_word'].replace('-','_')
            url_word_text1 = ''
            url_word_text2 = ''
            for word in url_word_old.split('_'):
                if len(url_word_text1+word)<=15:
                    url_word_text1 += word +' '
                else:
                    url_word_text2 += word +' '
            url_word_new = [url_word_text1.rstrip(), url_word_text2.rstrip()]
            # копируем уточнения
            utoch_list = yd['utoch'].copy()
            n=-1
            for utoch in utoch_list:
                n+=1
                text_utoch = ''
                # копируем заголовки
                for word in utoch.split():
                    if len(text_utoch+word)<=25:
                        text_utoch += word +' '
                    else:
                        break
                    utoch_list[n] = not_simbol_ads(text_utoch.rstrip())
            # меняем UTM
            utm = yd['utm'].copy()
            utm.update({'utm_source':'ads_poisk', 'utm_content':'gid|{adgroupid}|aid|{creative}|placement|{placement}', 'utm_term':'{keyword}'})
            # замена символов

            AdsPoisk(rk=str(id_rk_new), segment=str(id_seg_new), seg_name=seg['name'], name_rk=name_rk, zagolovok2=[zag2.replace('!', '.'), zag3.replace('!', '.')], bs=bs_list, url=yd['url'], url_word=url_word_new, text=[yd['text'].replace('!', '.'), ''], utoch=utoch_list, num = yd['num'], utm = utm, new_utm=yd['new_utm']).save()

    # снимаем лимит
    sum = int(data2['sum'])
    user = User.objects(id=current_user.id).first()
    for i in user.tarif:
        if sum != 0:
            if i[2] < sum:
                sum -= i[1]
                i[2] = 0
            else:
                i[2] -= sum
                break
    user.save()
    return jsonify({'id_rk': str(id_rk_new), 'id_folder':id_folder})


# ________________редактирование имен сегментов
@rk_yd.route('/up/red_name_seg', methods=['POST'])
@login_required
def red_name_seg():
    data2 = json.loads(request.data.decode('UTF-8'))
    id_rk = data2['id_rk']

    s = Segment.objects(rk=id_rk)
    return jsonify({'data': render_template('/up/red_name_seg.html', s=s)})

@rk_yd.route('/up/save_red_name_seg', methods=['POST'])
@login_required
def save_red_name_seg():
    data2 = json.loads(request.data.decode('UTF-8'))
    segment_id = data2['segment_id']
    segment_name = data2['segment_name']

    n=-1
    for id_seg in segment_id:
        n +=1
        seg = Segment.objects(id=id_seg).first()
        seg.name = segment_name[n]
        seg.save()
        if data2['rk_type'] == 'direct_rsy':
            for yd in YdRsy.objects(segment = id_seg):
                yd.seg_name = segment_name[n]
                yd.save()
        else:
            for yd in YDPoisk.objects(segment = id_seg):
                yd.seg_name = segment_name[n]
                yd.save()
    return jsonify({})

@rk_yd.route('/up/update_perenos', methods=['POST'])
@login_required
def update_perenos():

    user=User.objects(id=current_user.id).first()
    user.funkcional.append('perenos')
    user.save()

    return jsonify({})
