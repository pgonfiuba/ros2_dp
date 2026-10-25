# Doble péndulo con ROS 2 — Ayuda memoria

## 1. Preparación del workspace

### Ir al directorio de trabajo

```bash
cd ~/ros2_ws
```

### Compilar el paquete `dp`

```bash
colcon build --packages-select dp
```

### Cargar el workspace

```bash
source install/setup.bash
```

> Si el contenedor se inicia con el `entrypoint` del proyecto, ROS 2 y el workspace compilado se cargan automáticamente al abrir una terminal nueva. Después de compilar por primera vez, ejecutar `source install/setup.bash` en la terminal actual o abrir otra.

---

## 2. Visualización y simulación

### Visualización del robot solamente

```bash
ros2 launch dp display.launch.py
```

Permite visualizar el modelo del doble péndulo sin ejecutar la simulación física.

### Simulación con control

```bash
ros2 launch dp dp_sim.launch.py
```

Inicia la simulación integrada con ROS 2, Gazebo y RViz2, incluyendo el control del robot.

### Simulación a lazo abierto

El objetivo es imponer directamente torques en los ejes mediante el `effort_controller`, sin el control de posición.

```bash
ros2 launch dp dp_sim.launch.py
```

**Importante:** este comando es idéntico al de la simulación con control. Para que esta opción sea realmente de lazo abierto, el *launch* debe permitir desactivar el control de posición y activar el controlador de esfuerzo.

En la configuración caótica se utiliza `double_pendulum_caos.xacro`, que modifica las condiciones físicas del modelo:

- Sin rozamiento.
- Límites articulares amplios, para permitir múltiples vueltas.
- Límites de torque y velocidad ampliados, para no restringir artificialmente el comportamiento caótico.

Verificar que el *launch* esté seleccionando efectivamente ese Xacro y que el controlador de esfuerzo esté activo.

---

## 3. Inspección del modelo y de los tópicos

### Consultar el URDF cargado

```bash
ros2 param get /robot_state_publisher robot_description
```

Muestra la descripción del robot cargada en `robot_state_publisher`. Permite consultar los nombres de los *joints*, entre otros detalles del modelo.

### Consultar información de un tópico

```bash
ros2 topic info /joint_states
```

Muestra el tipo de mensaje y la cantidad de publicadores y suscriptores.

### Observar los mensajes de un tópico

```bash
ros2 topic echo /joint_states
```

Muestra los valores publicados en `/joint_states`, incluyendo posiciones, velocidades y esfuerzos, si están disponibles.

### Consultar los controladores activos

```bash
ros2 control list_controllers
```

Permite comprobar qué controladores están cargados y cuáles se encuentran activos.

---

## 4. Activar y desactivar el control de posición

### Desactivar el controlador

```bash
ros2 control set_controller_state position_controller inactive
```

### Activar el controlador

```bash
ros2 control set_controller_state position_controller active
```

La disponibilidad de este comando depende de la versión de `ros2_control` instalada. Si no está disponible, consultar:

```bash
ros2 control -h
```

### Alternativa mediante interfaz gráfica

```bash
ros2 run dp toggle_controller
```

Permite activar o desactivar el controlador mediante la interfaz del proyecto.

---

## 5. Imponer comandos de torque y posición

### Aplicar un torque

Publica un comando en el controlador de esfuerzo:

```bash
ros2 topic pub /effort_controller/commands \
  std_msgs/msg/Float64MultiArray \
  "data: [0.5, 0.0]"
```

El comando aplica los valores indicados a las articulaciones en el orden configurado en el controlador. Sin `--once`, el comando se publica repetidamente.

Para publicar una sola vez:

```bash
ros2 topic pub --once /effort_controller/commands \
  std_msgs/msg/Float64MultiArray \
  "data: [0.5, 0.0]"
```

### Imponer una referencia de posición

El controlador `position_controller` recibe un vector de posiciones objetivo:

```bash
ros2 topic pub --once /position_controller/commands \
  std_msgs/msg/Float64MultiArray \
  "data: [1.57, 0.0]"
```

Esto solicita las posiciones indicadas para las dos articulaciones. El comportamiento dinámico depende de la configuración del controlador y de sus ganancias.

### Enviar una trayectoria de posición

Para enviar una trayectoria mediante `joint_trajectory`:

```bash
ros2 topic pub --once /position_controller/joint_trajectory \
  trajectory_msgs/msg/JointTrajectory \
  "joint_names: ['joint1', 'joint2']
points:
- positions: [0.0, 1.57]
  time_from_start: {sec: 1}"
```

El punto de trayectoria especifica las posiciones deseadas al cumplirse un segundo. El controlador debe estar configurado para aceptar mensajes `JointTrajectory` en ese tópico.

---

## 6. Ajustar las ganancias del controlador

### Cambiar una ganancia en tiempo de ejecución

Ejemplo: modificar la ganancia proporcional del primer eje.

```bash
ros2 param set /position_controller gains.joint1.p 120.0
```

### Consultar todas las ganancias

```bash
ros2 param get /position_controller gains
```

Los cambios dinámicos dependen de que el controlador exponga esos parámetros y permita actualizarlos durante la ejecución.

---

## 7. Graficar variables de ROS 2

Ejecutar PlotJuggler:

```bash
ros2 run plotjuggler plotjuggler
```

Permite visualizar y comparar la evolución temporal de los tópicos publicados por el sistema.

---

## 8. Ajuste PID mediante Ziegler–Nichols (ZN)

### Eje 1

Parámetros críticos medidos:

$$
K_u = 120,\qquad T_u = 0.150\ \text{s}
$$

Para un PID clásico, las reglas de Ziegler–Nichols en lazo cerrado dan:

$$
K_p = 0.6K_u
$$

$$
K_i = \frac{1.2K_u}{T_u}
$$

$$
K_d = 0.075K_uT_u
$$

Con los valores medidos:

$$
K_p = 72,\qquad K_i = 960,\qquad K_d = 1.35
$$

### Eje 2

Parámetros críticos medidos:

$$
K_u = 90,\qquad T_u = 0.060\ \text{s}
$$

Aplicando las mismas reglas:

$$
K_p = 54,\qquad K_i = 1800,\qquad K_d = 0.405
$$

> Estos valores son una estimación inicial, no una garantía de estabilidad ni de buen desempeño. Conviene verificarlos en simulación y comprobar cómo interpreta el controlador las ganancias `p`, `i` y `d`. Las fórmulas anteriores corresponden a la forma PID paralela, con \(K_i\) y \(K_d\) expresados directamente.