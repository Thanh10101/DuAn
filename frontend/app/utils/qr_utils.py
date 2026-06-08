import os
import re
import qrcode

class QrUtils:

    @staticmethod
    def _safe_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "_", name)


    @staticmethod
    def _input_list(text):
        return [x.strip() for x in re.split(r'[\s,]+', text) if x.strip()]

    @staticmethod
    def SaveServer(**kwargs):
        try:
            folder = kwargs.get("folder")
            if not folder:
                raise Exception(f"Chưa nhập thư mục lưu")
            
            input = kwargs.get("input")
            data = QrUtils._input_list(input)
            if not data:
                raise Exception(f"Chưa nhập dữ liệu")
                
            os.makedirs(str(folder), exist_ok=True)
                
            for item in data:
                filename = QrUtils._safe_filename(item)
                img = qrcode.make(item)
                save_path = os.path.join(folder, f"{filename}.png")
                img.save(save_path)

            return f"Hoàn tất! Đã tạo {len(data)} QR trong thư mục '{folder}'"
        
        except Exception as e:
            raise Exception(f"QR utils - SaveServer: {e}")

    @staticmethod
    def SaveClient(**kwargs): 
        try:
            input = kwargs.get("input")
            data = QrUtils._input_list(input)
            if not data:
                raise Exception(f"Chưa nhập dữ liệu")
                
        
        except Exception as e:
            raise Exception(f"QR utils - SaveClient: {e}")
        
    @staticmethod
    def SawQr(input):
        try:
            data = QrUtils._input_list(input)
            if not data:
                raise Exception(f"Chưa nhập dữ liệu")
            
            images = {}
            for value in data:
                img = qrcode.make(value)
                images[value] = img
            
            return images

        except Exception as e:
            raise Exception(f"QR utils - SawQr: {e}")
        
        
   
    
    
            
            

           