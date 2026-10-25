# Simulación de la dinámica y el control de un doble péndulo

Este repositorio contiene modelos y simulaciones de un doble péndulo utilizando ROS 2, Gazebo y herramientas de visualización y control.

## Prerrequisitos

El entorno está preparado para Ubuntu 24.04 con ROS 2 Jazzy dentro de Docker. También puede funcionar en otras distribuciones Linux compatibles con Docker y con acceso a la interfaz gráfica del sistema anfitrión.

Se recomienda utilizar Ubuntu para simplificar la configuración de Docker y de las aplicaciones gráficas.

### Instalar Docker

Instalar Docker Engine:

```bash
sudo apt update
sudo apt install curl
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker "$USER"
```

Cerrar la sesión y volver a iniciarla para aplicar el cambio de grupo.

Documentación oficial: https://docs.docker.com/get-started/get-docker/

Instalar el complemento Docker Compose si todavía no está disponible:

```bash
sudo apt update
sudo apt install docker-compose-plugin
```

Documentación: https://docs.docker.com/compose/install/linux/

## Descargar el repositorio

```bash
git clone https://github.com/pgonfiuba/ros2_dp.git
cd ros2_dp
```

El entorno de ROS 2 se distribuye como una imagen Docker preconstruida, alojada en GitHub Container Registry (GHCR). No es necesario construir la imagen para utilizar las simulaciones.

## Iniciar el entorno

Desde el directorio `docker`:

```bash
cd docker
docker compose up 
```

La primera vez, Docker descargará la imagen si todavía no está disponible localmente. En ejecuciones posteriores reutilizará la imagen descargada.

El contenedor permanece en ejecución en segundo plano. No inicia automáticamente las simulaciones ni compila el workspace.

Para abrir una terminal dentro del contenedor:

```bash
docker compose exec ros2_dp bash
```

Los comandos siguientes se ejecutan dentro de esa terminal.

### Preparar el workspace

Al iniciar una terminal dentro del contenedor, el `entrypoint` carga automáticamente el entorno de ROS 2 y, si existe, el workspace compilado.

Para compilar los paquetes por primera vez, ejecutar:

```bash
cd /root/ros2_ws
colcon build --symlink-install
```

Una vez finalizada la compilación, cargar el workspace actualizado manualmente:

```bash
source install/setup.bash
```

El directorio `src` del repositorio está montado dentro del contenedor. Por lo tanto, los cambios realizados en el código desde el sistema anfitrión se reflejan inmediatamente en `/root/ros2_ws/src`. Cuando se modifica el código fuente, puede ser necesario volver a compilar los paquetes afectados y cargar nuevamente el workspace para utilizar las modificaciones.


## Simulación de péndulo doble con control PID

Es la simulación de control en lazo cerrado. Para iniciarla, desde una terminal dentro del contenedor:

```bash
ros2 launch dp dp_sim.launch.py
```

La simulación permite observar el comportamiento del doble péndulo y sus controladores mediante Gazebo y RViz.

![Simulación del doble péndulo en RViz](dp_RViz.png)

### Visualización con PlotJuggler

Para observar la evolución temporal de las variables, abrir otra terminal en el contenedor:

```bash
docker compose exec ros2_dp bash
```

Dentro ejecutar PlotJuggler:

```bash
ros2 run plotjuggler plotjuggler
```

En PlotJuggler se pueden seleccionar los tópicos publicados por la simulación para visualizar las señales de interés.

## Modificación dinámica de las ganancias

Es posible modificar las ganancias de los controladores PID de los `position_controllers` durante la simulación.

Con la simulación en lazo cerrado en ejecución, abrir otra terminal dentro del contenedor y ejecutar la aplicación gráfica:

```bash
ros2 run dp gui_controller.py
```

La aplicación permite modificar las ganancias y enviarlas al controlador. El efecto de los cambios puede observarse en RViz y mediante las señales registradas en PlotJuggler.

## Simulación del péndulo doble a lazo abierto

Para desactivar el control en lazo cerrado y permitir la aplicación de torques sobre los ejes:

```bash
ros2 launch dp dp_sim.launch.py closed_loop:=false
```

También se puede utilizar una definición del robot sin conexión a motores, sin rozamiento y sin límites de posición, velocidad y torque en los ejes. Esto permite observar comportamientos caóticos:

```bash
ros2 launch dp dp_sim.launch.py closed_loop:=false xacro_file:=dp_caos.xacro
```

## Simulación del péndulo libre

Es posible liberar el péndulo de la junta que fija su base al mundo. Esta configuración permite estudiar el movimiento del mecanismo sin una base inmóvil.

También se puede importar un mundo con un escritorio, de manera que el péndulo quede apoyado sobre él. Al accionar el mecanismo, este puede golpear el escritorio y provocar su movimiento.

```bash
ros2 launch dp dp_sim.launch.py closed_loop:=false xacro_file:=dp_loose.xacro world_name:=dp_escritorio.world
```

## Estructura de las definiciones del robot

Los principales archivos Xacro son:

- `dp_params.xacro`: define los parámetros cinemáticos y dinámicos del mecanismo y sus actuadores.
- `dp_base.xacro`: utiliza los parámetros anteriores para definir el robot y sus controladores de posición. También configura una interfaz para aplicar torques directamente a los ejes, útil para las simulaciones en lazo abierto.
- `dp_caos.xacro`: modifica los valores de rozamiento y los límites de los ejes para estudiar comportamientos caóticos.
- `dp_loose.xacro`: libera el robot de la junta fija al mundo. Esta configuración permite estudiar la interacción del mecanismo con su entorno.

## Actualizar la imagen Docker

La imagen se actualiza cuando se publica una nueva versión en GHCR. Para descargar explícitamente esa versión:

```bash
docker compose pull
```

Luego, recrear el contenedor:

```bash
docker compose up -d --force-recreate
```

No es necesario construir la imagen localmente para utilizar una versión publicada.

## Detener el entorno

Desde el directorio `docker` del repositorio:

```bash
docker compose down
```

Este comando detiene y elimina el contenedor, pero conserva la imagen descargada y los archivos del repositorio en el sistema anfitrión.

## Desarrollo

Para modificar los paquetes ROS 2, editar los archivos dentro de `src` desde el sistema anfitrión.

Después de realizar cambios en el código, entrar al contenedor, cargar el entorno de ROS 2 y recompilar cuando sea necesario:

```bash
cd /root/ros2_ws
colcon build
source install/setup.bash
```

Las modificaciones del código fuente no requieren reconstruir la imagen Docker. La imagen solo necesita actualizarse cuando cambian las dependencias del sistema, los paquetes instalados o la configuración del entorno.

