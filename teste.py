import pymysql

# Ajuste essas variáveis conforme seu ambiente
HOST     = 'localhost'
PORT     = 3306
USER     = 'root'
PASSWORD = 'Cooper2022'
DATABASE = 'kpis_becooper'

def test_connection():
    try:
        conn = pymysql.connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE,
            cursorclass=pymysql.cursors.Cursor
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            resultado = cursor.fetchone()[0]
            print(f"✅ Conexão OK! SELECT 1 retornou: {resultado}")
        conn.close()
    except Exception as e:
        print("❌ Erro ao conectar:", e)

if __name__ == "__main__":
    test_connection()
