# Guía Rápida para Usuarios Nuevos

## ¿Qué necesito antes de instalar?

Esta guía te ayudará a verificar que tu sistema tiene todo lo necesario para instalar Meowrch.

### 1. Verificar Prerrequisitos

Antes de comenzar la instalación, ejecuta este comando para verificar que tu sistema está listo:

```bash
python check_prerequisites.py
```

Este script verificará automáticamente:
- ✓ Arquitectura del sistema (x86_64, ARM, etc.)
- ✓ Python 3.8 o superior
- ✓ pip (gestor de paquetes de Python)
- ✓ git
- ✓ pacman (gestor de paquetes)
- ✓ Conexión a internet
- ✓ Espacio en disco

### 2. Si falta algo...

#### Si no tienes `pip`:
```bash
sudo pacman -S python-pip
```

#### Si no tienes `git`:
```bash
sudo pacman -S git
```

#### Si no tienes Python:
```bash
sudo pacman -S python
```

### 3. Instalar Meowrch

Una vez que todos los prerrequisitos estén listos:

```bash
# Ejecutar el instalador
sh install.sh
```

El instalador se encargará de:
- Detectar tu arquitectura automáticamente
- Instalar las dependencias de Python necesarias
- Configurar todo según tu hardware

## Solución de Problemas Comunes

### Error: "ModuleNotFoundError: No module named 'loguru'"

**Solución:**
```bash
# Instalar pip primero
sudo pacman -S python-pip

# Luego instalar las dependencias
pip install loguru inquirer --break-system-packages
```

### Error: "pip: command not found"

**Solución:**
```bash
sudo pacman -S python-pip
```

### Error: "git: command not found"

**Solución:**
```bash
sudo pacman -S git
```

## Probar Soporte ARM

Si estás en una Raspberry Pi u otro dispositivo ARM, puedes probar que todo funciona correctamente:

```bash
python test_arm_support.py
```

Este script:
- Verificará automáticamente si faltan dependencias
- Te preguntará si quieres instalarlas automáticamente
- Probará la detección de arquitectura
- Mostrará qué paquetes están disponibles para tu sistema

## ¿Necesitas Ayuda?

- **Telegram**: [t.me/meowrch](https://t.me/meowrch)
- **GitHub Issues**: [github.com/meowrch/meowrch/issues](https://github.com/meowrch/meowrch/issues)
- **Documentación completa**: Ver `ARM_INSTALLATION.md` para dispositivos ARM

---

**Nota**: Si eres nuevo en Linux, no te preocupes. Los scripts están diseñados para detectar problemas automáticamente y darte instrucciones claras sobre cómo solucionarlos.
