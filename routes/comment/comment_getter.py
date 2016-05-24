from flask_restful import Resource
from neo4j.v1 import ResultError
from connector import neo4j
from routes.utils import addargs


class GetCommentById(Resource):
    def get(self, comment_id):
        result = neo4j.query_neo4j("MATCH (find:comment {cid: %d}) RETURN find" % comment_id)
        try:
            return result.single()['find'].properties, 200
        except ResultError:
            return "ERROR : Cannot find comment with cid: %d" % comment_id, 200


class GetAllComments(Resource):
    def get(self):
        req = "MATCH (find:comment) RETURN find"
        req += addargs()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append(record['find'].properties)
        return comments


class GetAllCommentsByAuthor(Resource):
    def get(self, author_id):
        req = "MATCH (author:user {uid: %d})-[:authorship]->(c:comment) RETURN c" % author_id
        req += arglimit()
        result = neo4j.query_neo4j(req)
        comments = []
        for record in result:
            comments.append(record['c'].properties)
        return comments
