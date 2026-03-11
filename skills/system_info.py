"""
JARVIS Built-in Skill — System Info
Display system stats: CPU, memory, disk, processes
"""

import platform
import os

SKILL_NAME = "system_info"
SKILL_DESCRIPTION = "Show system information — CPU, memory, disk usage, uptime"
SKILL_TRIGGERS = ["system info", "system stats", "cpu", "memory usage", "disk space", "uptime", "system status"]


def run(user_input: str, context: dict) -> str:
    """Get system information."""
    try:
        import psutil

        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()

        # Memory
        mem = psutil.virtual_memory()
        mem_total = mem.total / (1024 ** 3)
        mem_used = mem.used / (1024 ** 3)
        mem_percent = mem.percent

        # Disk
        disk = psutil.disk_usage("/")
        disk_total = disk.total / (1024 ** 3)
        disk_used = disk.used / (1024 ** 3)
        disk_percent = disk.percent

        # Uptime
        import datetime
        boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.datetime.now() - boot_time
        uptime_str = str(uptime).split(".")[0]  # remove microseconds

        # GPU (nvidia-smi if available)
        gpu_info = _get_gpu_info()

        report = f"""🖥️ **System Status**

**OS:** {platform.system()} {platform.release()} ({platform.machine()})
**Hostname:** {platform.node()}
**Uptime:** {uptime_str}

**CPU:** {cpu_percent}% usage ({cpu_count} cores)
**RAM:** {mem_used:.1f} / {mem_total:.1f} GB ({mem_percent}%)
**Disk:** {disk_used:.1f} / {disk_total:.1f} GB ({disk_percent}%)"""

        if gpu_info:
            report += f"\n**GPU:** {gpu_info}"

        # Top processes by memory
        top_procs = sorted(
            psutil.process_iter(["name", "memory_percent"]),
            key=lambda p: p.info.get("memory_percent", 0) or 0,
            reverse=True,
        )[:5]

        report += "\n\n**Top Processes (by RAM):**"
        for proc in top_procs:
            name = proc.info.get("name", "?")
            mem_pct = proc.info.get("memory_percent", 0) or 0
            report += f"\n  • {name}: {mem_pct:.1f}%"

        return report

    except ImportError:
        return "❌ psutil not installed. Run: pip install psutil"
    except Exception as e:
        return f"❌ Error getting system info: {e}"


def _get_gpu_info() -> str:
    """Try to get GPU info from /proc (no subprocess needed)."""
    try:
        # Read from /proc if NVIDIA driver is loaded
        nvidia_dir = "/proc/driver/nvidia/gpus"
        if os.path.isdir(nvidia_dir):
            gpus = os.listdir(nvidia_dir)
            if gpus:
                info_path = os.path.join(nvidia_dir, gpus[0], "information")
                if os.path.isfile(info_path):
                    with open(info_path, "r") as f:
                        for line in f:
                            if line.startswith("Model:"):
                                return line.split(":", 1)[1].strip()
        return ""
    except (OSError, PermissionError):
        return ""

