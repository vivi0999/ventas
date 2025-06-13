from flask import Flask, render_template, request, redirect, session, make_response

from config.conexion import conexion
from fpdf import FPDF
app=Flask(__name__)
app.secret_key="mi clave"
def mostrarTodo():
    cursor=conexion.cursor()
    sql="select * from dbcliente"
    cursor.execute(sql)
    datos=cursor.fetchall()
    return datos

def mostrarCliente(id):
    cursor=conexion.cursor()
    sql="select * from dbcliente where id_dbcliente=%s"
    cursor.execute(sql,(id,))
    datos=cursor.fetchone()
    return datos

@app.route('/')
def index():
    if'usuario' in session:
       datos=mostrarTodo()
       return render_template('formulario.html', mostrar=datos)
    return render_template("login.html")

@app.route('/registro', methods=['GET','POST'])
def registro():
    nombre=request.form['txtnombre']
    nit=request.form['txtnit']
    cursor=conexion.cursor()
    sql="INSERT INTO dbcliente(nombre,nit) values(%s, %s)"
    cursor.execute(sql,(nombre,nit))
    conexion.commit()
    cursor.close
    mostrar=mostrarTodo()
    return render_template('formulario.html',mostrar=mostrar)



@app.route('/actualizar_cliente', methods=['post'])
def actualizar_cliente():
    id=request.form['txtid']
    nombre=request.form['txtnombre']
    nit=request.form['txtnit']
    cursor=conexion.cursor()
    sql="update dbcliente set nombre=%s , nit=%s where id_dbcliente=%s"
    cursor.execute(sql,(nombre,nit,id))
    conexion.commit()
    cursor.close
    return redirect('/')
@app.route('/actualizar/<id>')
def actualizar(id):
    cursor=conexion.cursor()
    sql="select * from dbcliente where id_dbcliente=%s"
    cursor.execute(sql,(id,))
    dato=cursor.fetchone()
    cursor.close
    return render_template('actualizar.html',dato=dato)

@app.route('/eliminar/<id>')
def eliminar(id):
    cursor=conexion.cursor()
    sql="delete from dbcliente where id_dbcliente=%s"
    cursor.execute(sql,(id,))
    conexion.commit()
    cursor.close
    return redirect('/')

@app.route('/comprar/<id>')
def comprar(id):
    datos=mostrarCliente(id)
    return render_template('comprar.html',id=id , datos=datos)


@app.route('/comprar', methods=['post'])
def insertarcompra():
    id=request.form['txtid']
    producto=request.form["txtproducto"]
    cantidad=request.form['txtcantidad']
    costo=request.form['txtcosto']
    print(f"ID recibido: {id}, Producto: {producto}, Cantidad: {cantidad}, Costo: {costo}")

    cursor=conexion.cursor()
    sql="INSERT INTO dbcompra(producto,cantidad,costo,iddbcliente) values(%s, %s,%s, %s)"
    cursor.execute(sql,(producto,cantidad,costo,id))
    conexion.commit()
    cursor.close
    mostrar=mostrarTodo()
    return render_template('formulario.html',mostrar=mostrar)

@app.route('/vercompras/<id>', methods=['get'])
def vercompras(id):
    cursor=conexion.cursor()
    sql="select * from dbcompra where iddbcliente=%s"
    cursor.execute(sql,(id,))
    datos=cursor.fetchall()
    return render_template('vercompras.html',datos=datos)
 
@app.route('/buscar', methods=['get'])
def buscar():
    buscar=request.args.get('txtbuscar')
    cursor=conexion.cursor()
    sql="select * from dbcliente where nombre like %s"
    cursor.execute(sql,(buscar+'%',))
    mostrar=cursor.fetchall()
    return render_template('formulario.html',mostrar=mostrar)

@app.route('/login', methods=['GET','POST'])
def login():
    mensaje=''
    if request.method =='POST':
        user=request.form['txtuser']
        clave=request.form['txtclave']

        cursor=conexion.cursor()
        sql='select id_usuario, user,clave from tbusuario where user=%s AND clave=%s' 
        cursor.execute(sql,(user,clave))
        usuario=cursor.fetchone()
        cursor.close()
        
        if usuario:
            session['usuario']=usuario[1]
            session['clave']=usuario[2]
            return redirect('/')
        else:
            mensaje="usuario o contraseña incorrecto"
    return render_template('login.html',mensaje=mensaje)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')





@app.route('/reporte/<id>')
def generar_pdf(id):
    cursor = conexion.cursor()

    sql = """
    SELECT c.nombre, c.nit, co.producto, co.cantidad, co.costo
    FROM dbcompra co
    INNER JOIN dbcliente c ON co.iddbcliente = c.id_dbcliente
    WHERE co.iddbcliente = %s
    """
    cursor.execute(sql, (id,))
    datos = cursor.fetchall()
    cursor.close()

    if not datos:
        return "No se encontraron compras para este cliente", 404

    nombre_cliente = datos[0][0]  # El nombre viene en la primera columna
    nit_cliente = datos[0][1]  # El NIT viene en la

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="REPORTE DE COMPRAS", ln=True, align="C")
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Cliente: {nombre_cliente}", ln=True)
    pdf.cell(200, 5, txt=f"NIT: {nit_cliente}", ln=True)
    pdf.ln(5)

    # Cabecera de la tabla
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(60, 10, "Producto", 1)
    pdf.cell(30, 10, "Cantidad", 1)
    pdf.cell(30, 10, "Costo", 1)
    pdf.cell(40, 10, "Total", 1)
    pdf.ln()

    # Datos
    pdf.set_font("Arial", '', 10)
    for fila in datos:
        _, _, producto, cantidad, costo = fila
        total = float(cantidad) * float(costo)
        pdf.cell(60, 10, str(producto), 1)
        pdf.cell(30, 10, str(cantidad), 1)
        pdf.cell(30, 10, f"{costo:.2f}", 1)
        pdf.cell(40, 10, f"{total:.2f}", 1)
        pdf.ln()

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=reporte_compras.pdf'
    return response
@app.route('/usuario')
def usuario():
    return render_template('usuario.html')

@app.route('/usuario', methods=['POST'])
def insertarUsuario():
    usuario = request.form['txtusuario']
    clave = request.form['txtclave']
    rol = request.form['txtrol']
    cursor = conexion.cursor()
    sql = "INSERT INTO tbusuario (user, clave, rol) VALUES (%s, %s, %s)"
    cursor.execute(sql, (usuario,clave,rol))
    conexion.commit()
    cursor.close()
    return redirect('/')


if __name__=='__main__':
    app.run(debug=True)