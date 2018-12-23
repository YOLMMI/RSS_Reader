#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import feedparser
import re
import sqlite3
import sys
import os
import wx
import wx.html2
from ObjectListView import ObjectListView, ColumnDefn

conn = sqlite3.connect("db.sqlite")
cursor = conn.cursor()

class RSS(object):
	def __init__(self, title, link, website, summary, all_data):
		self.title = title
		self.link = link
		self.all_data = all_data
		self.website = website
		self.summary = summary
		
def insert_sth_smw(name, link, category):
	sql = "INSERT INTO pages VALUES (?,?,?)"
	cursor.executemany(sql, [(name, link, category)])
	conn.commit()

def select_sth():
	sql = "SELECT name, link, category FROM pages"
	cursor.execute(sql)
	return cursor.fetchall()

class RssPanel(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.NO_FULL_REPAINT_ON_RESIZE)
		self.data = []
 
		lbl = wx.StaticText(self, label="URL канала:")
		lbl2 = wx.StaticText(self, label="Поиск:")
		self.rssSearch = wx.TextCtrl(self, value="")
		# self.rssSearch2 = wx.TextCtrl(self, value="")
		
self.rssUrlTxt = wx.TextCtrl(self, value="https://lenta.ru/rss")		
		searchBtn = wx.Button(self, label="Поиск по названию")
		searchBtn.Bind(wx.EVT_BUTTON, self.searchTitle)
		searchBtn2 = wx.Button(self, label="Поиск по содержанию")
		searchBtn2.Bind(wx.EVT_BUTTON, self.searchSummary)
		resetSearchBtn = wx.Button(self, label="Сбросить поиск")
		resetSearchBtn.Bind(wx.EVT_BUTTON, self.searchReset)
		urlBtn = wx.Button(self, label="Загрузить")
		urlBtn.Bind(wx.EVT_BUTTON, self.get_data)
 
		self.rssOlv = ObjectListView(self, 
									 style=wx.LC_REPORT|wx.SUNKEN_BORDER)
		self.rssOlv.SetEmptyListMsg("Пусто")
		self.rssOlv.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select)
		self.rssOlv.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_double_click)
		self.summaryTxt = wx.html2.WebView.New(self)
 
		self.wv = wx.html2.WebView.New(self)
		
		self.listoffeeds = []
		
		toolbar2 = wx.ToolBar(self)
		qtool = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('book-add.png'), "Добавить категорию")
		qtool2 = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('book_open-add.png'), "Добавить новость в список")
		qtool3 = toolbar2.AddTool(wx.ID_ANY, '', wx.Bitmap('book_open.png'), "Открыть список")

		toolbar2.Realize()

		toolbar2.Bind(wx.EVT_TOOL, self.enterCategory, qtool)
		toolbar2.Bind(wx.EVT_TOOL, self.save_page, qtool2)
		toolbar2.Bind(wx.EVT_TOOL, self.new_window, qtool3)

		rowSizer = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer.Add(lbl, 0, wx.ALL, 5)
		rowSizer.Add(self.rssUrlTxt, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer.Add(urlBtn, 0, wx.ALL, 5)
 
		vSizer = wx.BoxSizer(wx.VERTICAL)
		vSizer.Add(self.rssOlv, 1, wx.EXPAND|wx.ALL, 5)
		vSizer.Add(self.summaryTxt, 1, wx.EXPAND|wx.ALL, 5)
		
		rowSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer1.Add(lbl2, 0, wx.ALL, 5)
		rowSizer1.Add(self.rssSearch, 1, wx.EXPAND|wx.ALL, 5)
		rowSizer1.Add(searchBtn, 0, wx.ALL, 5)
		rowSizer1.Add(searchBtn2, 0, wx.ALL, 5)
		rowSizer1.Add(resetSearchBtn, 0, wx.ALL, 5)

		dispSizer = wx.BoxSizer(wx.HORIZONTAL)
		dispSizer.Add(vSizer, 1, wx.EXPAND|wx.ALL, 5)
		
		rowSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		rowSizer2.Add(dispSizer, 0, wx.EXPAND|wx.ALL, 5)
		rowSizer2.Add(self.wv, 2, wx.EXPAND|wx.ALL, 5)
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		mainSizer.Add(toolbar2, 0 , wx.RIGHT)
		mainSizer.Add(rowSizer, 0, wx.EXPAND)
		mainSizer.Add(rowSizer1, 0, wx.EXPAND)
		mainSizer.Add(rowSizer2, 1, wx.EXPAND|wx.ALL)
		
		self.SetSizer(mainSizer)
		self.update_display(self.data)

	def enterCategory(self, event):
		global category
		dlog=wx.TextEntryDialog(None,"Введите категорию")
		dlog.ShowModal()
		category=dlog.GetValue()
		
	def new_window(self, event):
		window = wx.Frame(None, -1, "Все записи")
		list_view = wx.ListCtrl(window, -1, style = wx.LC_REPORT) 
		list_view.InsertColumn(0, 'Название', width = 100) 
		list_view.InsertColumn(1, 'Ссылка', wx.LIST_FORMAT_RIGHT, 100) 
		list_view.InsertColumn(2, 'Категория', wx.LIST_FORMAT_RIGHT, 100) 
		for i in select_sth(): 
			index = list_view.InsertStringItem(sys.maxsize, i[0]) 
			list_view.SetStringItem(index, 1, i[1]) 
			list_view.SetStringItem(index, 2, i[2])
		window.Show()

	def save_page(self, event):
		obj = self.rssOlv.GetSelectedObject()
		name = obj.title
		link = obj.link
		insert_sth_smw(name, link, category)

	def get_data(self, event):
		msg = "Загрузка данных..."
		busyDlg = wx.BusyInfo(msg)
		rss = self.rssUrlTxt.GetValue()
		feed = feedparser.parse(rss)
		website = feed["feed"]["title"]
		for key in feed["entries"]:
			title = key["title"]
			link = key["link"]
			summary = key["summary"] if "summary" in key else "Нет"
			self.data.append(RSS(title, link, website, summary, key))
 
		busyDlg = None
		self.update_display(self.data)
	
	def searchTitle(self, event):
		search_list = []
		for key in self.data:
			title = key.title
			result = re.search('\s*%s' % self.rssSearch.GetValue(), title)
			if result != None:
				search_list.append(key)

		self.update_display(search_list)

	def searchSummary(self, event):
		search_list1 = []
		for key in self.data:
			summary = key.summary
			result1 = re.search('\s*%s' % self.rssSearch.GetValue(), summary)
			if result1 != None:
				search_list1.append(key)

		self.update_display(search_list1)

	def searchReset(self, event):
		self.update_display(self.data)

	def on_double_click(self, event):
		obj = self.rssOlv.GetSelectedObject()
		self.wv.LoadURL(obj.link)
 
	def on_select(self, event):    
		obj = self.rssOlv.GetSelectedObject()
		html = "<html><body>%s</body></html>" % obj.summary
		self.summaryTxt.SetPage(html, "")

	def update_display(self, data):
		self.rssOlv.SetColumns([
			ColumnDefn("Название", "left", 200, "title"),
			ColumnDefn("Сайт", "left", 200, "website"),
			])
		self.rssOlv.SetObjects(data)


class RssFrame(wx.Frame):
	def __init__(self):
		wx.Frame.__init__(self, None, title="RSS Reader", size=(1200,800))
		panel = RssPanel(self)
		self.Show()
 

if __name__ == "__main__":
	app = wx.App(False)
	frame = RssFrame()
	app.MainLoop()
