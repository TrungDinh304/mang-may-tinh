#Import thư viện socket để sử dụng các hàm liên quan đến socket (listen(), accept(), close()....)
import socket
#Import thư viện Threading (Đa luồng) để xử lý nhiều Client Connection đến Server cùng 1 lúc
import threading
#Import thư viện os là thư viện chứa các lỗi có thể xảy ra khi lập trình và tìm đường dẫn thư mục đang làm việc hiện tại 
import os

#Khai báo thông tin của Host address và Port Sử Dụng
HOST = '127.0.0.1'
PORT = 8080

#Tạo Socket Server với dạng địa chỉ IPv4 và giao thức TCP/IP (Có Kết Nối)
SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#Xóa những dòng thông tin trước đó, để Terminal chỉ hiện những thông tin về Connetion và Request hiện tại mà Webserver đang xử lý
os.system('cls')

#Bind Server Socket đã tạo ở trên lên, Nếu lỗi thì in thông báo ra ternimal 
try:
    SERVER.bind((HOST,PORT))
    #In lên Terminal xem WebServer đang chạy tại địa chỉ nào
    print(f'== Server running on http://{HOST}:{PORT} ==')
    #Nếu socket gặp lỗi thì sẽ báo lên terminal: 
except socket.error as e:
    print(f'\n-Socket error: {e}\n')
    
#Hàm lấy kích thước bytes của file
def get_size(file_name):
    #Đưa con trỏ về cuối file
    file_name.seek(0,2) 
    size = file_name.tell()
    file_name.close()
    return size  

#Hàm trả về http_header (Thông tin trong response_header) cho từng loại header_type tương ứng
def http_header(header_type):
    if header_type == '200':
        header = 'HTTP/1.1 200 OK\r\n'
    elif header_type == '404':
        header = 'HTTP/1.0 404 page not found\r\n'
    elif header_type == '401':
        header = 'HTTP/1.1 401 Unauthorized\r\n'
    return header

#Hàm trả về response_header tương ứng với từng loại content_type
def response_header(header_type, Content_type, file_size, connection_type):
    message_header = http_header(header_type)
    message_header += f'Content-type: {Content_type}\r\n'
    message_header += f'Connection: {connection_type}\r\n'
    message_header += f'Content-Length: {file_size}\r\n'
    message_header += '\r\n'
    message_header = message_header.encode()
    return message_header

#Hàm đọc nội dung file và chuyển data đã đọc về dưới dạng nhị phân (byte)(có http header ở trước nội dung)
def read_file(file_url, header_type, Content_type, file_size, connection_type):
    f = open(file_url, 'rb')
    # Gán http header vào trước nội dung file
    f_data = response_header(header_type, Content_type, file_size, connection_type)
    f_data += f.read()
    f.close()
    return f_data

# == 6. MULTIPLE REQUESTS. ==
#Hàm handle để xử lý Request từ Client. Parse Request Và Gửi Trả Data về
def handle(client, addr):
    
    #Thông báo có 1 connection từ Client đến Webserver
    print(f'\n[ CLIENT {addr} HAS CONNECTED ]')
    
    while True:
        #Nhận data là Request từ Client
        data = client.recv(1024).decode()
        #Nếu không có data thì thoát khỏi hàm (không xử lý tiếp nữa)
        if not data: 
            print(f'[ CLIENT {addr} CLOSED THE CONNECTION ]\n')
            break
        
        # Nếu có data thì phân tích Request Từ Data nhận về
        print('* Request received:')
        request_line = data.split('\r\n')[0]
        request_method = request_line.split(' ')[0]
        request_url = (request_line.split(' ')[1]).strip('/')
        connection_type = 'close'#(data.split('Connection: ')[1]).split('\n')[0]

        print(f'    -Client: {addr}')
        print(f'-Data: \n{data}')
        print(f'    -Request line: {request_line}')
        print(f'    -Request method: {request_method}')
        print(f'    -Request url: {request_url}')
        print(f'    -Request Connection type: {connection_type}')
        
        # == 3. TẢI ĐƯỢC PAGE INDEX.HTML == 
        #Nhận đường dẫn thư mục đang làm việc (Tức thư mục chứa các file cần đọc và send đến client)
        file_path=os.path.dirname(__file__)
        file_path=file_path.replace("\\",'/') + '/'
        print('    -Absolute directory name: ', file_path)
        
        #Nếu method nhận được là GET:      
        if request_method == 'GET':
            #Với mỗi loại request_url ( loại file cần đọc), cần trả về các thông tin url (đường dẫn file); content_type và header_type tương ứng
            if request_url == '' or request_url == 'index.html':
                url = file_path + 'index.html'
                Content_type = 'text/html'
                header_type = '200'
            elif (request_url.split('/')[0] == 'css'):
                url = file_path + request_url
                Content_type = 'text/css'
                header_type = '200'         
            elif request_url == 'favicon.ico':
                url = file_path + request_url
                Content_type = 'image/x-icon'
                header_type = '200'
            elif(request_url.split('/')[0] == 'images'):
                url = file_path + request_url
                header_type = '200'
                Content_type = 'image/jpeg' 
            elif(request_url.split('/')[0] == 'avatars'): 
                url = file_path + request_url
                header_type = '200'
                Content_type = 'image/png'
            else:
                # == 4. LỖI PAGE ==
                #Nếu Load Page Không Đúng Thì Trả Về 404.html
                header_type = '404'
                url = file_path + '404.html'
                Content_type = 'text/html'
                print('* Error 404: File not found *')
            
        # == 4. ĐĂNG NHẬP ==
        #Nếu method nhận được là POST:
        if request_method == 'POST':
            #Tách chuỗi uname và psw từ data
            login_line = data.split('uname')[1]

            #Tách lấy riêng uname và psw
                #Tách lấy user_name
            user_name=login_line.split('&')[0]
            user_name=user_name.split('=')[1]
                #Tách lấy password
            password=login_line.split('&')[1]
            password=password.split('=')[1]

            print(f'        +User Name: {user_name}')
            print(f'        +Password: {password}')

            #Kiểm tra uname và pws nếu đúng trả về images.html, nếu sai trả về 401.html
            if user_name == "admin" and password == "123456":
                url = file_path + 'images.html' 
                Content_type = 'text/html'
                header_type = '200'
                print('    -Signed In Successfully.')
            else:
                #Nếu Đăng Nhập Không Đúng Thì Trả Về 401.html
                header_type = '401'
                url = file_path + '401.html'
                Content_type = 'text/html'
                print('* Error 401: Unauthorized *')
        
        #Lấy kích thước file trả về    
        file_size = get_size(open(url,'rb'))
        print(f'    -File size: {file_size}\n')
        
        #SendBackData (nhị phân) là dữ liệu đọc từ hàm read_file (bao gồm response_header và nội dung file đọc tương ứng)  
        send_Back_Data = read_file(url,header_type, Content_type, file_size, connection_type)
        
        #Gửi nội dung data đã đọc lại cho client
        client.send(send_Back_Data)
        
    #Đóng Kết Nối Client
    client.close()


# == 1. KẾT NỐI == 
# == 2. QUẢN LÝ KẾT NỐI. ==
#Cho Mở Kết Nối Server Để Lắng Nghe Kết Nối Từ Client
def start_server():
    #Đợi kết nối từ Client
    SERVER.listen()

    # == 7. MULTIPLE CONNECTIONS. ==
    while True:
        #Chấp nhận Kết Nối từ Client 
        connection, address = SERVER.accept()
        
        #Thread dùng để xử lý nhiều connection cùng 1 lúc
        thread = threading.Thread(target= handle, args=(connection, address))
        thread.start()
    
if __name__ == '__main__':  
    start_server()