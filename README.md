# Bienestar & Tecnología
Este repositorio almacenará el código relacionado a la medición y análisis de variables fisiológicas (HR & HRV) provenientes de los sensores Polar H10 y Verity Sense. Además, de la integración de estas medidas con TouchDesigner mediante el protocolo de comunicación OSC.

# Instalación
- [ ] Descargue e instale Anaconda siguiendo las instrucciones dadas en  [este](https://docs.anaconda.com/anaconda/install/index.html) link.

- [ ] Se recomienda usar el editor de texto Vscode, ya que este software integra la lineo de comandos de github. Para descargar Vscode siga las instrucciones de instalación dadas en [este](https://code.visualstudio.com/download) link.

- [ ] Descargue git corriendo el siguiente comando en una ventana de terminal:
    ```
        conda install -c conda-forge git
    ```

- [ ] Clone el repositorio de github corriendo el siguiente comando (Asegúrese de estar en el folder en que quisiera almacenar el repositorio):
    ```
        git clone https://github.com/juanpbotero98/DosiMOEMS_GUI.git    
    ```
    Dado que el repositorio es privado se deben verificar las credenciales siguiendo las instrucciones dadas en la ventana de comandos.

- [ ] Descargue e instale los dependencias necesarias para el funcionamiento del código usando uno de los siguientes comandos (asegúrese de estar en la carpeta del repositorio):
    ```
        conda env create -f Environment/environment.yml
        conda create -n <environment-name> --file bienestar-tec.txt
    ```
    Si utiliza el primer comando el ambiente creado se llamará bienestar-tec.

- [ ] Active el ambiente de Anaconda corriendo el siguiente comando:
    ```
        conda activate dosiMOEMS
    ```

- [ ] Verifique la instalación corriendo la interfaz gráfica, utilizando el siguiente comando:
    ```
        python3 Python\GUI_V1.py
    ```

# Links relevantes
* pyHRV GitHub: https://github.com/PGomes92/pyhrv
* pyHRV Documentation: https://pyhrv.readthedocs.io/en/latest/index.html 
