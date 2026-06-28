# 单独一个线程用于检测 GPU 数量
import time
import traceback

from PySide6.QtCore import QThread, Signal
from videotrans.configure.config import logger
from videotrans.util.gpu_diagnostics import diagnose_gpu

class AiLoaderThread(QThread):
    gpu_io = Signal(str)

    def run(self):
        try:
            _st = time.time()
            diag = diagnose_gpu()
            logger.debug(f"[GPU] {diag.summary}; " + " | ".join(diag.details))
            from . import gpus
            _count = gpus.getset_gpu()
            logger.debug(f"找到 {_count} 个 Nvidia GPUs, 耗时: {int(time.time() - _st)}s")
            self.gpu_io.emit("end")
        except Exception as e:
            err = traceback.format_exc()
            logger.exception("[GPU] GPU 检测失败，继续使用 CPU fallback", exc_info=True)
            self.gpu_io.emit(f'{e},{err}')
