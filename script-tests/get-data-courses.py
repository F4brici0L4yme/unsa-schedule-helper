import requests

url = "http://extranet.unsa.edu.pe/sisacad/escuela/plan_estudios_datos.php3?codi_depe=446&cplan=2017"
answer = requests.get(url)
print(answer.status_code)
# print(answer.text[:1000])
# print(answer.url)

from bs4 import BeautifulSoup
soup = BeautifulSoup(answer.text, "html.parser")
tables = soup.find_all("table") # there's 2 
# table1 = tables[0]
data_table = tables[1] # the [0] was just a selector

#print(table1.prettify()[:1000])
#print("*******************************************************************************************")
#print(table2.prettify()[:1000])

rows = data_table.find_all("tr")
for row in rows[:15]:
    print(row.get_text(separator= "|", strip= True))

