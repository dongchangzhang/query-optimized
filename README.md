# query-optimized - sql优化

对以下三个语句进行优化

```sql
SELECT [ ENAME = 'Mary' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT )
```
查询树如下：
![tree1]()


优化后如下：
![tree2]()
```sql
PROJECTION [ BDATE ] ( SELECT [ ENAME = 'John' & DNAME = 'Research' ] ( EMPLOYEE JOIN DEPARTMENT ) )
```
请查看tree2*xx.pdf
```sql
SELECT [ ESSN = '01' ] ( PROJECTION [ ESSN , PNAME ] ( WORKS_ON JOIN PROJECT ) )

```
请查看tree3xx.pdf
