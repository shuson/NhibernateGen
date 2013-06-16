#!usr/bin/env
#
#Nhibernate xml cs file generator v 1.0
#Auther Shuson

import pyodbc

#set up connection and get cursor
con_String = "DRIVER={SQL Server};SERVER=.;DATABASE=TEST;UID=sa;PWD=sa"
conn = pyodbc.connect(con_String)
cursor = conn.cursor()

#set mapping basics
tableName = 'Table_Test'
namespace = 'shuson.NhibernateGen.Entities'
assembleName = 'NhibernateGen'

className = tableName.replace('_','')
csFile = open(className+'.cs','w')
xmlFile =open(className+'.hbm.xml','w')

#set database and c# data type
dataDict = {'int':'int','char':'string','varchar':'string','nvarchar':'string','datetime':'DateTime','bit':'bool'}

#locate key_name of Table_Test
cursor.execute("select key_name from information_schema.constraint_column_usage where table_name = ？ and constraint_name like 'PK%'",table_name)
key_name = cursor.fetchone().key_name

#initialize cs xml file
csFile.write('using System;\n\n')
csFile.write('namespace %s\n' %(namespace))
csFile.write('{\n')
csFile.write('\tpublic class %s' %(className))
csFile.write('{\n')

xmlFile.write('<?xml version="1.0" encoding="utf-8"?>\n')
xmlFile.write('<hibernate-mapping assembly="%s" namespace="%s" xmlns="urn:nhibernate-mapping-2.2">\n' %(assemblyName,namespace))
xmlFile.write('\t<class name="%s" table="%s" lazy="true" >\n' % (className, tableName))

#retrieve data structure from database
cursor.execute("""SELECT SC.COLUMN_NAME, SC.COLUMN_DEFAULT, SC.IS_NULLABLE, SC.DATA_TYPE,SC.CHARACTER_MAXIMUM_LENGTH AS LENGTH, CAST(P.value AS nvarchar(200)) AS MS_DESC 
  FROM information_schema.columns AS SC
	JOIN sys.tables AS T ON SC.TABLE_NAME = T.name
	JOIN sys.columns AS C ON T.object_id = C.object_id AND C.name = SC.COLUMN_NAME
	LEFT JOIN sys.extended_properties AS P ON C.column_id = p.minor_id AND P.major_id = T.object_id
	WHERE SC.table_name = ? """, tableName)
rows = cursor.fetchall()

# convert database type to c# and write to cs xml file
for r in rows:
	dataType = dataDict[r.DATA_TYPE]
	if r.IS_NULLABLE == "YES" and dataType != 'string':
		dataType+='?'
	csFile.write('\t\tpublic virtual %s %s { get; set; }\n\n' % (dataType, r.COLUMN_NAME))
	property_type = 'id' if r.COLUMN_NAME == key_name else 'property'
	xmlFile.write('\t\t<%s name="%s">\n' % (property_type, r.COLUMN_NAME))
	column_info = '\t\t\t<column name="%s" sql-type="%s' % (r.COLUMN_NAME, r.DATA_TYPE)
	if (r.LENGTH):
		column_info += '(max)' if r.LENGTH == -1 else '" length="%s' %(str(r.LENGTH))
	column_info += '" not-null="true" />\n' if r.IS_NULLABLE == 'YES' else '" not-null="false" />\n'
	xmlFile.write(column_info)
	xmlFile.write('\t\t</%s>\n' % (property_type))

#override cs object class
csFile.write('\t\tpublic override string ToString()\n')
csFile.write('\t\t{\n')
csFile.write('\t\t\treturn this.%s.ToString();\n' % (key_name))
csFile.write('\t\t}\n')

#complete ending part of cs xml file
csFile.write('\t}\n')
csFile.write('}\n')

xmlFile.write('\t</class>\n')
xmlFile.write('</hibernate-mapping>')

csFile.close()
xmlFile.close()

