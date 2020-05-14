import openpyxl

from layers.exporters.excel_templates import excel_templates

path = "C:\\Users\\clittle\\Downloads\\mobile.xlsx"

# To open the workbook
# workbook object is created
wb_obj = openpyxl.load_workbook(path)

# Get workbook active sheet object
# from the active attribute
sheet_obj = wb_obj.active







et = excel_templates('mobile')
wb = et.export()
wb.save("C:\\Users\\clittle\\Desktop\\demo.xlsx")
