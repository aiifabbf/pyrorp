
# Pyrorp - Python Implementation for Remote Object Reference Protocol

- - -

## Introduction

Remote Object Reference Protocol, known as RORP, is intended for simpler control on remote(or local, which may be located in a separate namespace on the same machine, e.g. process A and B) objects over the web. This protocol is a replacement for Remote Procedure Call, known as RPC, which is largely employed, for unsafety, un-symmetric(it has a clear difference between the server and client and only client can send requests to operate on the server but the server is unable to request anything from the client) low transparency and low-speed.

1. ### Abstract

	RORP is designed to be highly abstract, which means it does not care about the specific data transfer approach nor specific platform. In general, RORP is defined as a sequence of keyword dictionary. TCP, UDP(just remember to make sure the data is sent altogether:) or even SMTP, can be the base data transfer protocol. RORP is not meant to be single-platform-occupied nor single-lang-implemented, and pyrorp is just one Python implementation. The reason why we choose Python to make the very first implementation is that Python is highly abstract on top level, easy for developers' idea to be realised. 

