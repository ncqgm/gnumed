# Copyright (C) 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018  Rickard Lindberg, Roger Lindberg
#
# This file is part of Timeline.
#
# Timeline is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Timeline is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Timeline.  If not, see <http://www.gnu.org/licenses/>.


from timelinelib.general.observer import Observable


class Transactions(Observable):

    def __init__(self, initial_value, initial_name="", history_size=10):
        Observable.__init__(self)
        if history_size < 1:
            raise ValueError("history_size is to small (must be at least 1)")
        self._history_size = history_size
        self._history = [(initial_name, initial_value)]
        self._current_index = 0
        self._current_transaction = None

    @property
    def value(self):
        if self._current_transaction is not None:
            return self._current_transaction.value
        else:
            return self._history[self._current_index][1]

    @property
    def status(self):
        return (
            self._current_index,
            self._current_transaction is not None,
            list(self._history)
        )

    def clear(self):
        self.ensure_not_in_transaction()
        self._history = [self._history[self._current_index]]
        self._current_index = 0
        self._notify()

    def move(self, index):
        self.ensure_not_in_transaction()
        if index < 0 or index >= len(self._history):
            raise ValueError("Index does not exist in history")
        self._current_index = index
        self._notify()

    def new(self, name):
        self._current_transaction = Transaction(
            self,
            name,
            self.value,
            self._current_transaction
        )
        return self._current_transaction

    def commit(self, transaction):
        self.ensure_is_current(transaction)
        self._current_transaction = transaction.parent
        if self._current_transaction is None:
            self._history = self._history[:self._current_index + 1]
            self._history.append((transaction.name, transaction.value))
            self._history = self._history[-self._history_size:]
            self._current_index = len(self._history) - 1
            self._notify()
        else:
            self._current_transaction.value = transaction.value

    def rollback(self, transaction):
        self.ensure_is_current(transaction)
        self._current_transaction = transaction.parent

    def ensure_is_current(self, transaction):
        if transaction is not self._current_transaction:
            raise TransactionError(
                "Operation on {0!r} is not allowed "
                "because it is not the current transaction".format(
                    transaction
                )
            )

    def ensure_not_in_transaction(self):
        if self._current_transaction is not None:
            raise TransactionError(
                "Operation is not allowed "
                "because transaction {0!r} is active".format(
                    self._current_transaction
                )
            )


class TransactionError(Exception):
    pass


class Transaction(object):

    def __init__(self, transactions, name, value, parent):
        self._transactions = transactions
        self._name = name
        self._value = value
        self._parent = parent

    def __repr__(self):
        return "{0}(name={1!r}, ...)".format(
            self.__class__.__name__,
            self._name
        )

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._transactions.ensure_is_current(self)
        self._value = value

    @property
    def updater(self):
        return ValueUpdater(self)

    @property
    def parent(self):
        return self._parent

    def commit(self):
        self._transactions.commit(self)

    def rollback(self):
        self._transactions.rollback(self)

    def __enter__(self):
        return self.updater

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()


class ValueUpdater(object):

    def __init__(self, transaction):
        self._transaction = transaction

    def __getattr__(self, name):
        def updater(*args, **kwargs):
            self._transaction.value = getattr(
                self._transaction.value,
                name
            )(*args, **kwargs)
        return updater
