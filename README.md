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
        git clone https://github.com/juanpbotero98/HRV-Bienestar-Tecnologia.git   
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
        conda activate bienestar-tec
    ```

- [ ] Verifique la instalación corriendo la interfaz gráfica, utilizando el siguiente comando:
    ```
        python3 Python\GUI_V1.py
    ```

# Como correr la simulación OSC o el Demo de biofeedback

- [ ] Abra Anaconda Command Promot y active el ambiente usando el siguiente comando:
    ```
        conda activate bienestar-tec
    ```
    
- [ ] Dirigase a la carpeta del repositorio y entre a la carpeta de Demos:
    ```
        cd <Directorio a HRV-Bienestar-Tecnologia> (Ej. "C:\Users\Bienestar\Documentos\HRV-Bienestar-Tecnologia")
        cd Demos
    ```

## Simulación OSC
- [ ] Corra la simulación usando el siguiente comando:
    ```
        python OSC_Simulation.py --ip <ingrese su ip> --port <puerto OSC (default=8000)> --time <tiempo de simulación> --intervalo <intervalo de envio en segundos o fracciones de segundo> 
    ```
    Un ejemplo de ese comando:         
    ```
        python OSC_Simulation.py --ip 255.255.255.255 --port 8000 --time 120 --intervalo 0.5
    ```

## Demo Biofeedback
- [ ] Para correr el demo debe primero aveiguar la dirección MAC del sensor que se este usando, para esto corra el siguiente comando: 
    ```
        python BLE_Scanner.py
    ```
    Debería ver un impresión en pantalla similar a la siguiente: 
    ```
        EA:F6:8F:5B:90:CF: Polar H10 9A333525
        finished
    ```
    Copie la dirección que acompaña al nombre del sensor, en este caso "EA:F6:8F:5B:90:CF". Esta dirección es unica para cada sensor y es indispensable para correr el demo.

- [ ] Corra el demo usando el siguiente comando:
    ```
        python BioFeedback_Demo.py --ip <ingrese su ip> --mac <ingrese la dirección obtenida en el punto anterior> --port <puerto OSC (default=8000)> --time <tiempo de simulación> --intervalo <intervalo de envio en segundos o fracciones de segundo> 
    ```
    Un ejemplo de ese comando:         
    ```
        python OSC_Simulation.py --ip 255.255.255.255 --mac --port 8000 --time 120 --intervalo 0.5
    ```    

# Actualización de los archivos, para futuras versiones:
- [ ] Abra Anaconda Command Prompt y active el ambiente usando el siguiente comando:
    ```
        conda activate bienestar-tec
    ```
    
- [ ] Dirigase a la carpeta del repositorio y entre a la carpeta de Demos:
    ```
        cd <Directorio a HRV-Bienestar-Tecnologia> (Ej. "C:\Users\Bienestar\Documentos\HRV-Bienestar-Tecnologia")
    ```

- [ ] Descargue e instale los nuevos archivos:
    ```
        git pull 
    ```


# Links relevantes
* pyHRV GitHub: https://github.com/PGomes92/pyhrv
* pyHRV Documentation: https://pyhrv.readthedocs.io/en/latest/index.html 
