#from diff_match_patch import diff_match_patch
#
#dmp = diff_match_patch() 
#
#diff = dmp.diff_main("Пóчему́-то э́то не удало́сь.", "Пoчему-то это не удалось.")
#print(diff)
#html = dmp.diff_prettyHtml(diff)
#with open("diff.html", "w", encoding="utf-8") as f:
#    f.write(html)

from difflib import unified_diff

unified_dif = unified_diff(["Пóчему́-то э́то не удало́сь."], ["Пoчему-то это не удалось."])
print(next(unified_dif))