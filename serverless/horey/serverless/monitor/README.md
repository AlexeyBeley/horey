


#Monitor

#Worker:
lambda_handler.py:
   class Worker(MonitoredLambda)
      def main()
Worker().run()

#Monitored Lambda
lambda_handler.py
   class MonitoredLambda:
      def run():
          write_begin_to_db()
          self.main()
          write_end_to_db()

#Watchdog
lambda_handler.py
    class MonitoredLambda:
        def run():
            read_from_db()
            check_consistency()