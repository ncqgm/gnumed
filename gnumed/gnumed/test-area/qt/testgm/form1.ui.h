/****************************************************************************
** ui.h extension file, included from the uic-generated form implementation.
**
** If you wish to add, delete or rename functions or slots use
** Qt Designer which will update this file, preserving your code. Create an
** init() function in place of a constructor, and a destroy() function in
** place of a destructor.
*****************************************************************************/
#include <qtimer.h>
/**
  Note on dataBrowser update()  findPatientDataTable.refresh() connection.
  if the dataset in findPatientDataTable changes , findPatientDataTable.currentChanged() might be called , and the 
  dataBrowser may have it's view changed, if the dataBrowser's update button signals findPatientDataTable.
  This looks like a lost update . Easiest thing is to not signal findPatientDataTable.
  
  */

void Form1::saveLastNotes() {
	lastPatientId = getPatientId();
	saveAndLoadCurrentProgressNotes();

}


void Form1::init() {   
    clearLinkedUI();
    adjustUIAppearance();
    startProgressNoteTimer();
    connect( this, SIGNAL(close()), this, SLOT(saveLastNotes()) ); 
}

void Form1::startProgressNoteTimer() {
    QTimer*  notesTimer = new  QTimer(this);
    connect( notesTimer, SIGNAL(timeout()), SLOT(timeoutSaveNotes()) ); 
    notesTimer->start(5000); // update every 5 seconds
}

void Form1::Form1_usesTextLabelChanged(bool) {

}
void Form1::patientDataView_destroyed(QObject*) {
	qDebug("Destroyed patient data view");
}

void Form1::fileNew()
{
    enum TabPosition {
	Login, FindPatient, PatientDetail
    };
    
    mainTabWidget->setCurrentPage(PatientDetail);
}


void Form1::fileOpen()
{

}


void Form1::fileSave()
{

}


void Form1::fileSaveAs()
{

}


void Form1::filePrint()
{

}


void Form1::fileExit()
{

}


void Form1::editUndo()
{

}


void Form1::editRedo()
{

}


void Form1::editCut()
{

}

void Form1::editPaste()
{

}


void Form1::editFind()
{

}


void Form1::helpIndex()
{

}


void Form1::helpContents()
{

}


void Form1::helpAbout()
{

}



void Form1::selectPatientForEdit()
{
    qDebug("inSelectPatientForEdit()");
    QSqlRecord* record = findPatientDataTable->currentRecord();
    /** need to place a Guard against invalid currentRecord */
    if (record == 0)
	    return;

    qDebug(QString("selectPatientForEdit() calling changePatientId(%1)").arg(record->value("id_patient").toUInt() ) );
    changePatientId(record);
    
}

/** This function will change all the clinical UI according to the
  patient id value found by Form1.getPatientId()
  */

void Form1::setPatientIdInRecord( QSqlRecord * record )
{
    record->setValue("id_patient", QVariant( getPatientId() ) ); 
 }	


void Form1::changePatientId(const QSqlRecord * record )	
{
    qDebug("in ChangePatientId");
    if (record == 0)
	return;
    setPatientId( record->value("id_patient").toUInt());
} 


void Form1::setPatientId(uint id)
{
    if (patientId == id)
	return;
    patientId = id;
    lCDNumber1->display(QString("%1").arg(getPatientId()) );
    updatePatientIdFilter(id);
}


uint Form1::getPatientId()
{
    return patientId;
}

void Form1::updatePatientIdFilter(uint id)
{
    QPtrList<QDataTable> tables;
    getClinicalQDataTables(tables);

   QString filterString = QString("id_patient = %1").arg(id);

   for (QDataTable* dataTable = tables.first(); dataTable; dataTable= tables.next() ) {
       dataTable->setFilter( filterString   );
   }
   for (QDataTable*  dataTable = tables.first(); dataTable; dataTable= tables.next() ) {
         dataTable->refresh();
   }
   
   dataBrowser1->setFilter(filterString);
   dataBrowser1->refresh();
   
   dataBrowser1->first();
	   
   updateOldProgressNotes( );
   saveAndLoadCurrentProgressNotes( );
   
}


void Form1::insertPrimaryKeyInPatientRecord(QSqlRecord * record )
{
    record->setNull("id_patient");
    QSqlQuery query;
    query.exec("select nextval('id_patient_sequence')");
//    qDebug("size of select nextval=%d", query.size());
    query.first();
    QVariant  value = query.value(0);
  //  qDebug("nextval of id_patient = %ud" ,  value.toUInt());
    record->setValue("id_patient", value );
    
    changePatientId(record);
}



void Form1::setSequenceField( QSqlRecord *record, const QString& fieldName, const QString& sequenceName) {
    QSqlQuery query;
    query.exec("select nextval('" + sequenceName + "')");
    query.first();
    record->setValue( fieldName, query.value(0) );
}


/**
  returns a  QPtrList of QDataTables
  */
void Form1::getClinicalQDataTables( QPtrList<QDataTable> & tables) {
     tables.setAutoDelete(false);
     tables.append(pastHistoryDataTable);
     tables.append( prescriptionDataTable);
     tables.append( allergyDataTable);
     tables.append( investigationDataTable);
     tables.append( vaccinationDataTable );
  
}

void Form1::getAllQDataTables( QPtrList<QDataTable> & tables) {
	getClinicalQDataTables(tables);
	tables.append( findPatientDataTable);
}

void Form1::setPastHistoryId( QSqlRecord* record)
{
    setSequenceField( record, "id_history", "id_history_sequence"); 
}



void Form1::setPrescriptionId( QSqlRecord * record )
{
    setSequenceField( record, "id_prescription", "id_prescription_sequence");
    //statePrescriptionEdit = 0;
}


void Form1::setAllergyId( QSqlRecord * record )
{
    setSequenceField( record, "id_allergy", "id_allergy_sequence");
}


void Form1::setInvestigationId( QSqlRecord * record )
{
    setSequenceField( record, "id_investigation", "id_investigation_sequence"); 
}


void Form1::setVaccinationId( QSqlRecord * record )
{
    setSequenceField( record, "id_vaccination", "id_vaccination_sequence");
}


void Form1::updateOldProgressNotes( )
{
     QString buffer;
    
     QSqlQuery query;
     if (
	     !query.exec( QString("select id_progress_note, date_entered, notes, username from progress_note where id_patient = %1 order by date_entered , id_progress_note ")
			  .arg(getPatientId()) 
			  )  )  {
	 //TO-DO : manage failed query for finding old progress notes.
	 return; 
     }
     // "select id_progress_note, date_entered, notes, username from progress_note where id_patient = %1 and id_progress_note not in ( select max( id_progress_note) from progress_note where id_patient = %2 and date_trunc('day', date_entered) = date_trunc('day', now() )   ) order by date_entered"
     oldProgressTextEdit->setText( convertProgressNotesSqlQueryToString(&query, buffer) );
     
}

/**
  if  saves this version of the progress notes, including any unedited stuff entered earlier for this day by
  this person. if demoRecord is 0 , then the currentProgress notes aren't updated for the new patient.
  */
bool Form1::insertProgressNote( const QString & note, uint patient_id) {
    QSqlQuery query;
    if (lastNoteId == 0) {
	query.exec("select nextval('id_progress_note_sequence')");
	query.first();	
	QVariant id_note = query.value(0);
	QSqlQuery query2;
	bool result =  query2.exec( 
QString("insert into progress_note( id_patient,id_progress_note,  notes, date_entered) values ( %1, %2,  '%3', now() )").
	arg( patient_id) .arg(id_note.toUInt()).arg( note)
	);
	lastNoteId = id_note.toUInt();
	return result;
    }
    
    return query.exec(
	    QString("update progress_note set notes = '%1' where id_progress_note = %2").
	    arg(note).arg(lastNoteId) );
    
}


void Form1::saveAndLoadCurrentProgressNotes( )
{
    QSqlQuery query;
    
    
    // don't save if there is no lastPatient to save
    if ( lastPatientId.toString() != "none"  && currentProgressTextEdit->isModified() )  {
	
	
	uint lastId = lastPatientId.toUInt();
	
	QString note = currentProgressTextEdit->text().stripWhiteSpace();
	
	// get the last notes entered for the day
	query.exec(QString("select  notes from progress_note where  id_progress_note = (select max(id_progress_note) from progress_note where id_patient = %1 and username=user and date_trunc( 'day', now() ) = date_trunc( 'day', date_entered) )").arg( lastId) );
	
	
	    insertProgressNote( note, lastId);
	
	
	
    }
     
    // don't update if no next patient record ( means saving but not selecting)
    
    
    // update the last patient id to the current patient id
     QVariant id = QVariant(getPatientId());
     lastPatientId = id;
     
     // find the progress notes for today
     query.exec(
	     QString("select id_progress_note, date_entered, notes, username from progress_note where id_progress_note = ( select max(id_progress_note) from progress_note where id_patient=%1 and date_trunc( 'day',date_entered) = date_trunc('day', now()  )  )" ).arg(getPatientId() ) );
 
     // show the progress notes found for today.
     QString buffer;
     query.first();
     currentProgressTextEdit->setText( query.value(2).toString() );
     authorAndTimeLabel->setText( getAuthorAndTimeString( &query, buffer) );
     currentProgressTextEdit->setModified(false);
     lastNoteId = 0;
     
}

void Form1::timeoutSaveNotes() {
    qDebug("SAVING NOTES if modified");
    QString note;
    if (currentProgressTextEdit->isModified() ) {
	note = currentProgressTextEdit->text().stripWhiteSpace();
	insertProgressNote( note, getPatientId());
    }
}

/** for debugging of the query values.
  */
QString& Form1::debugQueryValues(QSqlQuery * query, QString &result) {
    QStringList list;
    for (int i = 0; query->value(i).isValid() ; ++i) {
	list.append( query->value(i).toString() );
    }
    result = list.join(", ");
    return result;
}

/** returns the progress notes locator details as a string.
  */
QString& Form1::getAuthorAndTimeString( QSqlQuery * query, QString & result) {
    result = query->value(1).asDateTime().toString() + QString("  ") + query->value(3).toString() ;
    return result;
}

/** converts a progress note row into a string like record for display in old progress notes ui. 
  */
QString& Form1::convertProgressNotesSqlQueryToString( QSqlQuery * query , QString & result) 
{
     QStringList notesList;
      QString debugValues;
      QString timeStr;
     while (query->next()) {
	
	 qDebug("Query values are " +debugQueryValues( query, debugValues));
	 QString notes = query->value(2).toString().stripWhiteSpace();
	 if (notes == "")
	     continue;
	 notesList.append(getAuthorAndTimeString( query, timeStr) );
	 notesList.append("===");
	 notesList.append( query->value(2).toString());
	 notesList.append("");
	 notesList.append("");
	 
     }
     result = notesList.join("\n");
     qDebug("Result should be " + result);
     return result;

}

/** sets the filter for patient demographic browse table.
  */
void Form1::setPatientNameFilter()
{
    qDebug("In setPatientNameFilter");
    QStringList names = QStringList::split(",",  searchPatientNameLineEdit->text());
    if (names.size() < 1) {
	findPatientFilter = "false";
	return;
    }
    if (names.size() == 1) {
	QStringList spacedNames = QStringList::split(" ",names[0]);
	if (spacedNames.size() > 1) {
		names[0] = spacedNames[0];
		names[1] = spacedNames[1];	
	}

    }
    while (names.size() < 2) 
	names.append("");
    for (int i = 0; i < 2; ++i) {
    	QString s =  names[i].stripWhiteSpace();
    	names[i] = s;
    }
    
    
    this->findPatientFilter = QString("lastnames like \'%1\%\' and firstnames like \'%2\%\'")  .arg(names[0]). arg( names[1] );
     
    qDebug("Before Set Filter");
    findPatientDataTable->setFilter(findPatientFilter);
    //QSqlCursor* cursor = findPatientDataTable->sqlCursor();
    //cursor->editBuffer()->clearValues();
    //cursor->select();
    qDebug("Before Refresh");
    /* On refresh(), selectionChanged() will be signalled  , and will 
     * try to invoke selectPatientForEdit() with invalid currentRecord() in
     * findPatientDataTable , throwing a seg fault, so need to guard
     * against this by testing for currentRecord() == 0 in selectionChanged() */
    findPatientDataTable->refresh(QDataTable::RefreshData);
    
    
}




void Form1::clearLinkedUI()
{
    setPatientId(0);
    //dataBrowser1->clearValues();
}


void Form1::setInvestigationDefaultDate(QSqlRecord * record)
{
    record->setValue("datetime_ordered", QVariant( QDateTime::currentDateTime()) );
}


void Form1::setPrescriptionDefaultDate( QSqlRecord *record )
{
    record->setValue("date_prescribed", QVariant( QDate::currentDate()) );
    record->setValue("date_commenced", QVariant(QDate::currentDate()) );
}

void Form1::setPastHistoryDefaultDate( QSqlRecord * )
{

}


void Form1::setAllergyDefaultDate( QSqlRecord * )
{

}


/** this hack function intercepts clicks on the first col ("print") and toggles it.
  any clicking on any other columns should be ignored, as this function will 
  interfere with the editing buffer , due to its call on primeUpdate().
  */
void Form1::togglePrintOnClickPrescription( int row, int col, int button , const QPoint& p)
{
    if ( col > 0 || button != 1 )  {// right-clicked, using the menu 
    
       return;
   }
    
    qDebug( QString("\nclicked on %1 , %2, button %3").arg(row). arg(col). arg(button) );
    QSqlCursor * cursor = prescriptionDataTable->sqlCursor();
    
     qDebug(QString("Mode is %1").arg(cursor->mode() ) );
    qDebug(QString("Cursor is at %1").arg( cursor->at() ) );
    QSqlRecord * record =  cursor->primeUpdate();
    record->setValue("print", QVariant(!record->value("print").toBool()) );
    cursor->update();
  
    //clear the editbuffer again
    cursor->primeInsert();
    cursor->select();
}

void Form1::printSelectedPrescriptions() {

}


void Form1::adjustUIAppearance()
{
    QValueList<int> vList;
    vList.append( splitter2->height()/2);
    vList.append(splitter2->height()/2);

    splitter2->setSizes( vList);
    splitter2->repaint();

}
