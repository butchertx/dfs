import time
import logging

logger = logging.getLogger(__name__)

class Timer:
    
    def __init__(self):
        self.start_times = {}
        self.cumul_times = {}
    
    def flag_start_time(self, timer_name: str):
        if timer_name not in self.start_times.keys():
            self.start_times[timer_name] = time.perf_counter()
        else:
            logger.warning(f'{timer_name} start time double-flagged')
        
    def flag_end_time(self, timer_name: str):
        if timer_name in self.start_times.keys():
            elapsed = time.perf_counter() - self.start_times.pop(timer_name)
            if timer_name in self.cumul_times.keys():
                self.cumul_times[timer_name] += elapsed
            else:
                self.cumul_times[timer_name] = elapsed
        else:
            logger.warning(f'{timer_name} end flagged without a start')
            
    def reset_timers(self):
        for timer_name in list(self.start_times):
            self.start_times.pop(timer_name)
        for timer_name in list(self.cumul_times):
            self.cumul_times.pop(timer_name)
            
    def print_timers(self):
        for timer_name in list(self.start_times):
            self.flag_end_time(timer_name)
        self.cumul_times['total time'] = sum(self.cumul_times.values())
        outstr = "Timer Results:"
        for timer_name, time_total in self.cumul_times.items():
            outstr += f"\n    {timer_name: >20}: {time_total:11.3f}s"
        print(outstr)