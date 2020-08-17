from app.main.Semantics.abs_sem import *
import time

class StageSemantics(AbsSemantics):
    """This class implements stage semantics. This is similar to seminaive
    semantics of deriving the delta tuples, \Delta(t), and deleting their
    regular counterparts, t, at the end of every stage of the evaluation process"""

    def __init__(self, db_conn, rules, tbl_names):
        super(StageSemantics, self).__init__(db_conn, rules, tbl_names)

    def find_mss(self):
        """implementation of end semantics where updates
        to the tables are at the end of each stage of the evaluation"""
        res = []  # added
        mss = set()
        changed = True
        prev_len = 0

        cnt = 1

        while changed:
            tp = set()
            for i in range(len(self.rules)):
                results = self.db.execute_query(self.rules[i][1])
                self.delta_tuples[self.rules[i][0]].update(results)
                mss.update([(self.rules[i][0], row) for row in results])
                tp.update([(self.rules[i][0], row, i) for row in results])
            res.append(tp)  # added
            changed = prev_len != len(mss)
            prev_len = len(mss)
            # update original tables at the end of each evaluation step
            for i in range(len(self.rules)):
                self.db.delete(self.rules[i], self.delta_tuples[self.rules[i][0]])
                self.db.delta_update(self.rules[i][0], self.delta_tuples[self.rules[i][0]]) # update delta table in db
            cnt += 1

        order = {t[0]:1 for t in mss}
        realRES = []

        tables = ['author', 'publication', 'writes', 'organization', 'cite']
        stat = {t: 0 for t in tables}

        for l in res:
            tp = set()
            for t in l:
                tp.add( (t[0], (t[0] + str(order[t[0]]),) + t[1], t[2]) )
                stat[t[0]] += 1
                order[t[0]] += 1
            realRES.append(tp)

        return realRES, 'placeholder', [stat['author'], stat['publication'], stat['writes'], stat['organization'], stat['cite']] #mss
