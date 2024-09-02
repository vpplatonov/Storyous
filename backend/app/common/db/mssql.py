import functools
from datetime import datetime
from typing import Generic, get_args, Union, Tuple, Optional, Dict, List, Any

import pymssql
import pyodbc
from fastapi_utils.api_model import PYDANTIC_VERSION, APIModel
from fastapi_utils.camelcase import camel2snake
from pydantic.tools import parse_obj_as

from common.config import T
from common.db.connect_sql import get_connection
from common.db.json_to_sql import JsonToSQL
from common.db.utils import (
    get_repository_for_model, APIModelSQL, COUNT_FIELD, NUM_UPDATE_FIELD,
    DB_PRIMARY_KEY, SQL_REPOSITORY_POSTFIX, DEFAULT_DB_NAME_SPACE
)

FOREIGN_KEY = "foreign_key"
PRIMARY_KEY = "primary_key"
QUERY_FIELD = "filter"


def reconnect_on_exception(func):
    """ decorator to deal with MSSQL OperationalError exception.
    Exception happened on cursor.execute() - not client.cursor().
    https://techcommunity.microsoft.com/t5/azure-database-support-blog/lesson-learned-359-tcp-provider-error-code-0x68-104/ba-p/3834127

    usage: wrap functions with body like this

        with self.client.cursor() as cursor:
            self._cursor_execute(
                sql_query,
                cursor,
                multi=True
            )
            data = self._fetch_one(cursor)

        return data
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        """ it wrapped method of class: self always present """
        while True:
            try:
                data = func(self, *args, **kwargs)
            except pyodbc.OperationalError as e:
                # must be wrapper with @lru_cache decorator
                get_connection.cache_clear()
                self.client = get_connection()
            else:
                break

        return data

    return wrapper


def with_transaction(func):
    """ Decorator for wrap DB transaction with rollback()/commit() """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            data = func(self, *args, **kwargs)
        except (pymssql.Error, pyodbc.Error) as e:
            self.client.rollback()
            print(str(e))
            raise CrudDataMSSQLError(str(e)) from e
        else:
            self.client.commit()
            return data

    return wrapper


class CrudDataMSSQLError(Exception):
    """ raise this exception for all CRUD data incompatibility """


class RepositoryMSSQL(Generic[T]):
    """ base model for MS SQL DB: pip install pymssql """

    model: APIModelSQL

    excluded_fields: set = {}
    name_space: str = DEFAULT_DB_NAME_SPACE
    table_prefix: str = ''
    primary_key = DB_PRIMARY_KEY
    pk_remove_on_create = True  # if pk is incremental / not defined externally

    def __init__(self):
        super(RepositoryMSSQL, self).__init__()

        self.client: Union[pyodbc.Connection, pymssql.Connection] = get_connection()
        self.model = get_args(self.__orig_bases__[0])[0]  # Magic
        self.json_to_sql = JsonToSQL(
            self,
            name_space=self.name_space,
            excluded=self.excluded_fields,
            table_prefix=self.table_prefix,
            primary_key=self.primary_key,
            pk_remove_on_create=self.pk_remove_on_create
        )

    @staticmethod
    def _set_context(user_id: int, stp_exec: str = 'story_api_set_context') -> str:
        """ Set session context with CONTEXT_INFO: MSSQL v12

        in stored procedure OR trigger (see Entities table triggers for ex.):
        
        DECLARE @myval int;
        DECLARE @myval_bin VARBINARY(4);
        SET @myval = 987654321;
        SET @myval_bin = CAST(@myval AS VARBINARY(4));
        SET CONTEXT_INFO @myval_bin;

        DECLARE @UserID int;
        DECLARE @userid_bin VARBINARY(4);
        SET @userid_bin = CONTEXT_INFO();
        SET @UserID = CAST(@userid_bin as int);

        SELECT  @UserID,
            CONVERT(int, CONTEXT_INFO()),
            CAST(SUBSTRING(CONTEXT_INFO(), 1, 4) AS int);
        GO

        :return: sql_query to add
        """

        # for pyodbc stored procedure created
        sql_query = f"EXEC [com].[{stp_exec}] {user_id};"

        return sql_query

    @staticmethod
    def _fetch_one(cursor: Union[pymssql.Cursor, pyodbc.Cursor]) -> Optional[Dict]:
        data = cursor.fetchone()
        if data and isinstance(data, pyodbc.Row):
            columns = [c[0] for c in cursor.description]
            data = dict(zip(columns, data))

        return data

    @staticmethod
    def _fetch_all(cursor: Union[pymssql.Cursor, pyodbc.Cursor]) -> Optional[List]:
        data = cursor.fetchall()
        if data and isinstance(data, list) and isinstance(data[0], pyodbc.Row):
            columns = [c[0] for c in cursor.description]
            data = [dict(zip(columns, dt)) for dt in data]

        return data

    @staticmethod
    def _cursor_execute(sql_query, cursor, multi=False, sql_div=';'):
        """ pyodbc can't execute multiple query at a time """

        if (isinstance(cursor.connection, pyodbc.Connection) and multi
                and sql_div in sql_query):

            # TODO: try find better solution
            sql_queries = sql_query.rsplit(sql_div, maxsplit=2)
            for query in sql_queries:
                if query:
                    cursor.execute(query)
        else:
            cursor.execute(sql_query)

    @staticmethod
    def _get_foreign_key(data: APIModelSQL, field: str) -> str:
        if PYDANTIC_VERSION[0] == "2":
            return data.model_fields[field].json_schema_extra.get(FOREIGN_KEY, None)
        else:
            # deprecated
            return data.__fields__[field].field_info.extra.get(FOREIGN_KEY, None)

    @staticmethod
    def _get_field_plugin(field_data: APIModelSQL) -> Optional[str]:
        """ get plugin name from field data """
        return field_data.__class__.__module__.replace("_sql", "")

    @staticmethod
    def _get_excluded_fields_data(data: T) -> Dict:
        """ helper for get APIModelSQL from fields """

        exclude_fields = {
            field for field, val in data.model_fields.items()
            if val.json_schema_extra and val.json_schema_extra.get(FOREIGN_KEY, None)
        }
        exclude_data = {key: getattr(data, key) for key in exclude_fields}

        return exclude_data  # ignore

    def _apply_excluded_fields_data(
            self,
            excluded_data: Dict,
            source_data: T,
            res: Dict,
            cursor: Union[pymssql.Cursor, pyodbc.Cursor]
    ) -> Optional[Dict]:
        """ Apply (Create) all APIModelSQL fields excluded on create step """

        rs = {}
        for field, ex_data in excluded_data.items():
            if ex_data is None or not ex_data:
                continue

            ex_data_elem = ex_data
            if isinstance(ex_data, list):
                ex_data_elem = ex_data[0]
            else:
                ex_data = [ex_data]
            repository = get_repository_for_model(
                model_type=ex_data_elem.__class__.__name__,
                prefix='',
                plugin=self._get_field_plugin(ex_data_elem)
            )
            foreign_key = self._get_foreign_key(source_data, field)

            # ex_data does not have fk objects
            if self._get_excluded_fields_data(ex_data_elem):
                repos = repository()
                for data in ex_data:
                    e_data = self._get_excluded_fields_data(data)
                    setattr(data, foreign_key, res[self.primary_key] or getattr(source_data, foreign_key))
                    result = repos.create_with_cursor(data, cursor)
                    if e_data:
                        res = self._apply_excluded_fields_data(
                            excluded_data=e_data,
                            source_data=data,
                            res=res,
                            cursor=cursor
                        )
            else:
                result = repository().create_many_with_cursor(
                    data=ex_data,
                    query={foreign_key: res[self.primary_key] or getattr(source_data, foreign_key)},
                    cursor=cursor
                )

            rs.update({field: result})

        return rs

    def _update_excluded_fields_data(
            self,
            excluded_data: Dict,
            source_data: T,
            res: Dict,
            cursor: Union[pymssql.Cursor, pyodbc.Cursor]
    ) -> Optional[Dict]:
        """ Update all APIModelSQL fields excluded on create step """

        rs = {}
        for field, ex_data in excluded_data.items():
            if ex_data is None or not ex_data:
                continue

            ex_data_elem = ex_data[0] if isinstance(ex_data, list) else ex_data
            repository = get_repository_for_model(
                model_type=ex_data_elem.__class__.__name__,
                prefix='',
                plugin=self._get_field_plugin(ex_data_elem)
            )

            foreign_key = self._get_foreign_key(source_data, field)
            query = {foreign_key: res[self.primary_key]}
            repos = repository()
            if isinstance(ex_data, list):
                repos.delete_with_cursor(query=query, cursor=cursor)
                result = repos.create_many_with_cursor(
                    data=ex_data,
                    query=query,
                    cursor=cursor
                )
            else:
                # TODO: check if ex_data has exclude_data = self._get_excluded_fields_data(ex_data)
                if model := repos.view(query):
                    model.__dict__.update(ex_data.dict())
                    result = repos.update_with_cursor(
                        model,
                        cursor=cursor,
                        query={self.primary_key: getattr(model, self.primary_key)}
                    )
                else:
                    setattr(ex_data, foreign_key, res[self.primary_key])
                    result = repos.create_with_cursor(
                        data=ex_data,
                        cursor=cursor
                    )

            rs.update({field: result})

        return rs

    @staticmethod
    def _get_converted_fields_data(data: T) -> Dict:
        """ helper for get APIModelSQL from fields """

        exclude_fields = {
            field for field, val in data.model_fields.items()
            if val.json_schema_extra and val.json_schema_extra.get(PRIMARY_KEY)
        }
        exclude_data = {key: getattr(data, key) for key in exclude_fields}

        return exclude_data  # ignore

    @staticmethod
    def _set_converted_field_data(data: T, convert_data: Dict):
        for field, c_d in convert_data.items():
            if c_d is None or isinstance(c_d, (int, str)):
                continue
            key = data.model_fields.get(field).json_schema_extra.get(PRIMARY_KEY)
            setattr(data, field, getattr(c_d, key))

    def select_insert_with_cursor(self, data: T, cursor: Union[pymssql.Cursor, pyodbc.Cursor]):
        res = self.view({self.primary_key: getattr(data, self.primary_key)})
        if res is None:
            return self.create_with_cursor(data, cursor)

        return {self.primary_key: res}

    def insert_update(self, data: T):
        """ TODO: ODBC MSSQL driver does not support more then 1 command at a time

        USE merge instead (one way for pyodbc drive):

            merge tablename with(HOLDLOCK) as target
                using (values ('new value', 'different value'))
                    as source (field1, field2)
                    on target.idfield = 7
                when matched then
                    update
                    set field1 = source.field1,
                        field2 = source.field2,
                        ...
                when not matched then
                    insert ( idfield, field1, field2, ... )
                    values ( 7,  source.field1, source.field2, ... )

        OR simplest way with IF EXISTS (two command in 1 line: if pymssql):

            UPDATE target SET col = tmp.col
            FROM target
            INNER JOIN #tmp ON <key clause>;
            INSERT target(...) SELECT ... FROM #tmp AS t
            WHERE NOT EXISTS (SELECT 1 FROM target WHERE key = t.key);

        """
        query = {self.primary_key: getattr(data, self.primary_key, None)}
        res = self.update(data, query)
        if not res or not res.get(NUM_UPDATE_FIELD, None):
            res = self.create(data)

        return res

    def _converted_select_insert(self, convert_data: dict, cursor: Union[pymssql.Cursor, pyodbc.Cursor]):
        """ Verify if pk object exists otherwise create it """

        res = []
        for key, c_data in convert_data.items():
            if isinstance(c_data, (str, int)):
                continue
            repository = get_repository_for_model(
                model_type=c_data.__class__.__name__,
                prefix='',
                plugin=self._get_field_plugin(c_data)
            )
            repos = repository()
            rs = repos.select_insert_with_cursor(c_data, cursor)
            res.append(rs)

        return res

    @reconnect_on_exception
    def exec_fetch_one(self, sql_query: str) -> Dict:
        """ for pymssql.Connection client """

        with self.client.cursor() as cursor:
            self._cursor_execute(
                sql_query,
                cursor,
                multi=True
            )
            data = self._fetch_one(cursor)

        return data  # ignore

    def exec_fetch_one_parse(self, sql_query: str) -> Optional[T]:
        data = self.exec_fetch_one(sql_query=sql_query)

        return self.model.model_validate(data) if data else None

    @reconnect_on_exception
    def exec_fetch_all(self, sql_query: str) -> List[Dict]:
        """ for pymssql.Connection client """

        with self.client.cursor() as cursor:
            self._cursor_execute(
                sql_query,
                cursor,
                multi=True
            )
            data = self._fetch_all(cursor)

        return data

    def index(self, **kwargs) -> Union[list[T], Tuple]:
        """ change kwargs[QUERY_FIELD] to kwargs["query"] """

        sql_query, sl_count_query = self.json_to_sql.get_mssql_select_count(
            query=kwargs.get(QUERY_FIELD, {}),
            **{k: v for k, v in kwargs.items() if k != QUERY_FIELD},
            primary_key=self.primary_key
        )

        data = self.exec_fetch_all(sql_query)
        data = parse_obj_as(list[self.model], data)

        if 'skip' in kwargs and 'limit' in kwargs:
            result = self.exec_fetch_one(sl_count_query)

            return data, result[COUNT_FIELD]

        return data

    def _get_key_dict(self, query: Union[str, int, dict]) -> Dict:
        """ convert key as syt or dict to dict with one key """

        if isinstance(query, str) or isinstance(query, int):
            query = {self.primary_key: query}
        elif isinstance(query, dict) and hasattr(query, self.primary_key):
            query = {self.primary_key: getattr(query, self.primary_key)}

        return query

    def view(self, query: Union[str, int, dict]) -> Optional[T]:
        """ if primary key _id - str; if primary other than _id: dict """

        query = self._get_key_dict(query)
        sql_query, _ = self.json_to_sql.get_mssql_select_count(
            query=query,
            primary_key=self.primary_key
        )
        return self.exec_fetch_one_parse(sql_query=sql_query)

    def _create_sql_query(self, data: Union[T, Dict]) -> str:
        raw_data = data
        if not isinstance(data, dict):
            raw_data = data.dict()
        if (pid := raw_data.get(self.primary_key, None)) is not None:
            raw_data[self.primary_key] = pid

        sql_query = self.json_to_sql.get_mssql_insert(
            sql_set=raw_data
        )

        return sql_query

    def create_with_cursor(self, data: Union[T, Dict], cursor: Union[pymssql.Cursor, pyodbc.Cursor]):
        sql_query = self._create_sql_query(data)
        self._cursor_execute(
            sql_query,
            cursor,
            multi=True
        )
        data = self._fetch_one(cursor)

        return data

    @with_transaction
    def create(self, data: Union[T, Dict]) -> Dict:
        sql_query = self._create_sql_query(data)
        sql_query = self.sql_before_execute(sql_query)
        data = self.exec_fetch_one(sql_query=sql_query)

        return data

    def normalize_exclude_data(self, exclude_data):
        """ Data normalization : example see  db/sources_sql """

        return exclude_data

    def converted_select_insert_batch(self, converted_data: Dict, cursor):
        # from field to class name
        res = {}
        for class_name, c_data_list in converted_data.items():
            c_data = c_data_list[0]
            repository = get_repository_for_model(
                model_type=c_data.__class__.__name__,
                prefix='',
                plugin=self._get_field_plugin(c_data)
            )
            repos = repository()
            pk = repos.primary_key
            c_data_list_unique_ids = {getattr(c_d, pk) for c_d in c_data_list}
            ids_in_db = repos._batch_exists_ids(c_data_list_unique_ids)
            c_data_list_unique_ids = c_data_list_unique_ids.difference(set(ids_in_db))

            # check if keys in DB by select
            if c_data_list_unique_ids:
                c_data_list_unique = []
                c_data_list_unique_added = set()
                for c_d in c_data_list:
                    if (pk_v := getattr(c_d, pk)) and pk_v in c_data_list_unique_added:
                        continue
                    c_data_list_unique_added.add(pk_v)
                    c_data_list_unique.append(c_d)
                rs = repos.create_many_with_cursor(
                    data=c_data_list_unique,
                    query={},  # nothing to update
                    cursor=cursor
                )
                res.update({class_name: rs})

        return res

    def _batch_exists_ids(self, ids: List[Union[int, str]]) -> List[Any]:
        list_res: List[T] = self.index(filter={self.primary_key: {'$in': ids}})
        ids = [getattr(t, self.primary_key) for t in list_res]

        return ids

    def create_batch_with_cursor(self, data_batch_list: List[T], cursor):
        """ Return num rows inserted """
        rs = self.create_many_with_cursor(
            data=data_batch_list,
            query={},  # nothing to update
            cursor=cursor
        )
        return rs

    def _apply_batch_excluded_fields_data(
            self,
            excluded_data: List[T],
            source_data: List[T],
            res: List[Dict],
            cursor
    ):
        res = {}

        NotImplementedError("")

        return res

    def converted_select_insert(self, convert_data, cursor: Union[pymssql.Cursor, pyodbc.Cursor]):
        """ must be implemented for apps specific """
        # rs = self._converted_select_insert(convert_data, cursor)
        # return rs

        return {}

    @staticmethod
    def _update_converted_data(converted_data, convert_data):
        for k, v in convert_data.items():
            if not issubclass(v.__class__, APIModel):
                continue
            key = v.__class__.__name__
            v = [v]
            if key in converted_data:
                v.extend(converted_data[key])
            converted_data.update({key: v})

    @with_transaction
    @reconnect_on_exception
    def create_batch_data_apply_excluded(self, data_batch, converted_data, exclude_data):
        res = {}
        with self.client.cursor() as cursor:
            # next line keep outside of SQL API: apps specific
            rs = self.converted_select_insert_batch(converted_data, cursor)  # ignore
            res.update(rs)
            rs = self.create_batch_with_cursor(data_batch, cursor)  # return num_rows inserted
            res.update(rs)
            if exclude_data and not self.pk_remove_on_create:  # PRIMARY keys already defined
                rs = self._apply_batch_excluded_fields_data(
                    excluded_data=exclude_data,
                    source_data=data_batch,
                    res=rs[self.primary_key],  # list of inserted keys
                    cursor=cursor
                )
                res.update(rs)

        return res

    def create_batch_with_fk(self, data_batch: List[T], excluded: bool = False):
        exclude_data = []
        converted_data = {}
        for i, data in enumerate(data_batch):
            if excluded:
                exclude_data.append(self._get_excluded_fields_data(data))  # foreign keys
            convert_data = self._get_converted_fields_data(data)  # primary keys
            self._set_converted_field_data(data_batch[i], convert_data)
            self._update_converted_data(converted_data, convert_data)

        res = self.create_batch_data_apply_excluded(data_batch, converted_data, exclude_data)

        return res

    @with_transaction
    @reconnect_on_exception
    def create_data_apply_excluded(self, data, exclude_data):
        """ it can be decorated with reconnect_on_exception """
        with self.client.cursor() as cursor:
            res = self.create_with_cursor(data, cursor)
            rs = self._apply_excluded_fields_data(
                excluded_data=exclude_data,
                source_data=data,
                res=res,
                cursor=cursor
            )
        return res

    def create_with_fk(self, data: T):
        """ Create API for 1:M fields """

        exclude_data = self._get_excluded_fields_data(data)  # foreign keys
        exclude_data = self.normalize_exclude_data(exclude_data)
        convert_data = self._get_converted_fields_data(data)  # primary keys
        self._set_converted_field_data(data, convert_data)

        res = self.create_data_apply_excluded(data, exclude_data)

        return res

    def create_many_with_cursor(
            self,
            data: List[Union[T, Dict, int, str]],
            query: Dict,
            cursor: Union[pymssql.Cursor, pyodbc.Connection]
    ) -> Dict:
        # ODBC driver has limitation 1000 row at a time
        sql_set_list = [d.model_dump() for d in data]
        sql_query = self.json_to_sql.get_mssql_insert_many(
            sql_set_list=sql_set_list,
            key_value=query
        )
        self._cursor_execute(
            sql_query,
            cursor,
            multi=True
        )
        # return num rows inserted: GET_SQL_NUM_ROWS
        result = self._fetch_one(cursor)

        return result

    @with_transaction
    def create_many(self, data: List[T], query: Dict) -> Dict:
        # ODBC driver has limitation 1000 row at a time
        sql_query = self.json_to_sql.get_mssql_insert_many(
            sql_set_list=[d.model_dump() for d in data],
            key_value=query
        )
        result = self.exec_fetch_one(sql_query=sql_query)

        return result

    def _update_sql_query(self, data: T, query: Union[dict, str]) -> str:
        if query is None:
            raise Exception(f'Unknown {QUERY_FIELD}')

        query = self._get_key_dict(query)

        if hasattr(data, 'updated_at'):
            data.updated_at = datetime.now()

        set_data = data.dict(exclude_unset=True)
        set_data.pop(self.primary_key, None)
        sql_query = self.json_to_sql.get_mssql_update(
            query=query,
            sql_set=set_data
        )

        return sql_query

    def update_with_cursor(
            self,
            data: T,
            cursor: Union[pymssql.Cursor, pyodbc.Cursor],
            query: Union[dict, str, int, T] = None
    ):
        sql_query = self._update_sql_query(data, query)
        self._cursor_execute(
            sql_query,
            cursor,
            multi=True
        )
        data = self._fetch_one(cursor)

        return data

    @with_transaction
    def update(self, data: T, query: Union[dict, str]) -> Dict:
        sql_query = self._update_sql_query(data, query)
        sql_query = self.sql_before_execute(sql_query)
        data = self.exec_fetch_one(sql_query=sql_query)  # return num rows updated (1)

        return data

    @with_transaction
    @reconnect_on_exception
    def update_data_update_excluded(self, data: T, exclude_data, query: Union[str, int, Dict] = None):
        """ can be wrapped with """
        query = self._get_key_dict(query or data)
        with self.client.cursor() as cursor:
            num_count = self.update_with_cursor(data, cursor, query)
            rs = self._update_excluded_fields_data(
                excluded_data=exclude_data,
                source_data=data,
                res=query,
                cursor=cursor
            )

        return num_count

    def update_with_fk(self, data: T, query: Dict):

        exclude_data = self._get_excluded_fields_data(data)
        exclude_data = self.normalize_exclude_data(exclude_data)
        convert_data = self._get_converted_fields_data(data)
        self._set_converted_field_data(data, convert_data)

        num_count = self.update_data_update_excluded(data, exclude_data, query)

        return num_count

    def delete_with_cursor(
            self,
            cursor: pymssql.Cursor,
            data: Optional[Union[T, dict]] = None,
            query: Dict = None
    ):
        sql_query = self.json_to_sql.get_mssql_delete_one(
            query=query or {self.primary_key: getattr(data, self.primary_key)}
        )
        self._cursor_execute(
            sql_query,
            cursor,
            multi=True
        )
        result = self._fetch_one(cursor)

        return result

    @with_transaction
    def delete(self, data: Optional[Union[T, dict]] = None, query: Dict = None):
        """ query for delete many rows """

        sql_query = self.json_to_sql.get_mssql_delete_one(
            query=query or {self.primary_key: getattr(data, self.primary_key)}
        )
        sql_query = self.sql_before_execute(sql_query)
        result = self.exec_fetch_one(sql_query=sql_query)   # return num rows deleted (1)

        return result

    def count(self, **kwargs) -> int:
        _, sql_count_query = self.json_to_sql.get_mssql_select_count(
            query=kwargs.get(QUERY_FIELD, {}),
            primary_key=self.primary_key
        )
        result = self.exec_fetch_one(sql_query=sql_count_query)

        return result[COUNT_FIELD]

    def exists(self, **kwargs) -> bool:
        return bool(self.count(**kwargs))

    def aggregate(self, pipeline) -> list[dict]:
        raise NotImplementedError(f"Method have not been supported for {pipeline=}")

    def sql_before_execute(self, sql_query: str) -> str:
        """ right place to override SQL query """

        return sql_query

    @classmethod
    def table_name(cls):
        # ClientsAndAuth -> clients_and_auth conversion

        table_name = str(cls.__name__).replace(SQL_REPOSITORY_POSTFIX, '')
        table_name = camel2snake(table_name)

        return table_name
