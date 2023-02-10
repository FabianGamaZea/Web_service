from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import mysql.connector

class Ui_MainWindow(object):
    sucursal = 'ZACATECAS'
    mes = '1'
    año = '2022'
    def conexion(self):
        miConexion = mysql.connector.connect( host='localhost', user= 'root', passwd='', db='pmn' )
        cur = miConexion.cursor()
        query = f"""SELECT DISTINCT
	pmn_sis_parametros_pagos_pendiente.parametros_pagos_pendiente_estatus_renovacion,
	pmn_datos_contratacion.contratacion_no_contrato,
    pagos_contratados.pagos_contratados_fecha_enque_pago,
	pmn_datos_contratacion.contratacion_fecha_fin_contrato_anterior,
	pmn_datos_contratacion.contratacion_sucursal,
	pagos_contratados.pagos_contratados_sucursal
FROM
	pmn_datos_contratacion
LEFT JOIN pmn_sis_parametros_pagos_pendiente ON pmn_datos_contratacion.contratacion_no_contrato = pmn_sis_parametros_pagos_pendiente.parametros_pagos_pendiente_no_contrato
LEFT JOIN pagos_contratados ON pmn_sis_parametros_pagos_pendiente.parametros_pagos_pendiente_id = pagos_contratados.pagos_contratados_parametro_fk_id
WHERE
	pagos_contratados.pagos_contratados_sucursal = '{self.sucursal}'
    AND MONTH(pagos_contratados.pagos_contratados_fecha_enque_pago)= {self.mes}
    AND YEAR(pagos_contratados.pagos_contratados_fecha_enque_pago) = {self.año}
    AND pagos_contratados.pagos_contratados_no_pago_actual = 1
    AND pagos_contratados.pagos_contratados_tipo = 'RENOVACION' """
        cur.execute(query)
        queryResult = cur.fetchall()  

        df = pd.DataFrame(queryResult)
        self.names = ['parametros_pagos_pendiente_estatus_renovacion',
                      'contratacion_no_contrato',
                      'contratacion_fecha_inicio_contrato_actual', 
                      'contratacion_fecha_fin_contrato_anterior', 
                      'contratacion_sucursal', 'pagos_contratados_sucursal']
        self.aux = []
     

        for index, row in df.iterrows():
            fechaAnterior = row[3]
            fechaActual = row[2]
     
            if fechaAnterior != None:
                dif = fechaActual - fechaAnterior
                if int(dif.days) > 365:
                    self.aux.append(row)
                                    
     
    def setupUi(self, MainWindow):
        self.conexion()
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(858, 498)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(40, 30, 661, 341))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(len(self.names))
        self.tableWidget.setRowCount(len(self.aux))
        for i in range(len(self.aux)):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setVerticalHeaderItem(i, item)
            
        for i in range(len(self.names)):
            item = QtWidgets.QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(i, item)    
            
          
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(750, 50, 81, 16))
        self.label.setMinimumSize(QtCore.QSize(0, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(750, 80, 101, 21))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CarteraVencida"))
        
        for i in range(len(self.names)):
            self.tableWidget.horizontalHeaderItem(i).setText(self.names[i])
            
        __sortingEnabled = self.tableWidget.isSortingEnabled()
        self.tableWidget.setSortingEnabled(False)
        con  = 0 
        for i in self.aux:
            con2 = 0
            for j in i:
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(j))
                self.tableWidget.setItem(con,con2,item) 
                con2 = con2+1
                #print(j)
            con = con +1
        self.tableWidget.setSortingEnabled(__sortingEnabled)
        self.label.setToolTip(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:14pt; vertical-align:super;\">Total:</span></p><p><br/></p></body></html>"))
        self.label.setText(_translate("MainWindow", "Total:"))
        self.label_2.setText(_translate("MainWindow", str(len(self.aux))))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())