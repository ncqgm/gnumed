import time

class model_util:
	def get_new_key(self):
		t = time.time() % 10000000
		t = long(t * 10)
		return t
	
	def validate_key(self, map):
		if not map.has_key('key'):
			return 0
		
		if str(map['key']).strip() == '':
			return 0
		return 1

	def delete(self, key, map):
		old = {}
		if map.has_key(key):
			old = map[key]
			del map[key]
		return	old

	def copy_map( self, map):
		amap = {}
		amap.update(map)
		return amap

	def update(self, data, target, others):
		key = data['key']
		all = []
		old = {}	
		all.extend(others)
		if target not in all:
			all.append(target)
		
		for x in all:
			if x.has_key(key):
				old = x[key]
				del x[key]
				break
		target[key] = data
		return old

	def copy_and_set_key (self, data):
		map = {}
		map.update(data)
		if not self.validate_key(map):
			map['key'] = self.get_new_key()
			#copy key to model
			data['key'] = map['key']
		return map	

	def check_has_mandatory_fields(self, fields,data):
		for x in fields:
			if not data.has_key(x):
				return 0
			if str(data[x]).strip() == '':
				return 0
		return 1	
			
			


class problems_model:
	def __init__(self):
		self.__init_data()
		self.util = model_util()

	def __init_data(self):
		self.past_history_map = {}
		self.active_problems_map = {}
		self.is_active_problem_update = 0
	
	def set_is_active_problem_update(self, value):
		self.is_active_problem_update = value <> 0 
	
	
	
	def add_problem( self, amap):
		if not self.util.check_has_mandatory_fields( ['condition'], amap):
			return {}

		map = self.util.copy_and_set_key(amap)
		
		if self.is_active_problem_update:
			return self.update_problems( data = map, target = self.active_problems_map, other = self.past_history_map)

		return self.update_problems( data = map, target =  self.past_history_map, other = self.active_problems_map)		

	def update_problems( self, data, target, other):
		self.util.update(data, target, [other])

	def remove_problem( self, key):
		old =   self.util.delete(key, self.active_problems_map)
		if old <> {}:
			return old
		
		return self.util.delete(key, self.past_history_map)


	def get_problems_map(self):
		if self.is_active_problem_update:
			return self.util.copy_map( self.active_problems_map)

		return self.util.copy_map (self.past_history_map)
	

	def get_active_problem( self, key):
		return self.get_problem_from(self.active_problems_map, key)

	def get_past_history(self, key):
		return self.get_problem_from(self.past_history_map, key)

	def get_problem_from(self, map, key):
		return map.get(key, {} )

class script_model:
	def __init__(self):
		self.__init_data()
	
	def __init_data(self):
		self.scripts_map = {}
		self.order_items = []
		pass

	def check_identity( self, info):
		#need to implem,ent
		return None	

	def add_session_script( self, script_info):
		copy_map = {}
		copy_map.update(script_info)
		old_key = self.check_identity(script_info)
		if old_key <> None:
			old = self.scripts_map[old_key]
			self.scripts_map[old_key] = copy_map
			return old

		t = time.time() % 10000000
		t = t * 10
		print "before insertion , scrip map = ", self.scripts_map
		self.scripts_map[long(t)] = copy_map
		print "***script map =", self.scripts_map
		return None

	def get_session_scripts( self):
		map = {}
		map.update( self.scripts_map)
		return map

	def set_list_order(self,  order = [] ):
		self.order_items = order

	def get_session_scripts_as_tuples_key_data(self):
		return self.get_session_scripts_as_mapped_lists().items()

	def get_session_scripts_as_mapped_lists(self):
		map = {}
		order_items = self.order_items
		if order_items == [] :
			order_items = [ 'generic_drug', 'strength', 'directions', 'prescription_reason' ]
		print "*** scripts_map = ", self.scripts_map.items()
		for k,v in self.scripts_map.items():
			list = []
			for key in order_items:
				list.append( v.get(key,'') )
			map[k] = list
		print "*** map resulting = ", map
		return map


	def delete_session_script( self, key):
		print "remove key =",key
		old = None
		if self.scripts_map.has_key(key):
			old = self.scripts_map[key]
			del self.scripts_map[key]
		return old	
	
class drug_model:
	def __init__(self):
		self.__init_data()
	
	def __init_data(self):
		self.angina_drugs = {
		'nitrates': [ 'glyceryl trinitrate', 'isosorbide dinitrate', 'isosorbide mononitrate'],
		'other antianginal' : [ 'nicorandil', 'perhexeline'] }

		self.hypertension_drugs = {
		'thiazide diuretics' : [ 'bendrofluazide', 'chlorthalidone', 'hydroochlorothiazide', 'indapamide' ],
		'potassium-spairing diuretics' : ['amiloride', 'spironolactone' ],
		'beta-blockers': ['atenolol', 'carvedilol', 'labetalol', 'esmolol', 'metoprolol', 'oxrpenolol', 'pindolol', 'propranolol', 'sotalol' ],
		'angiotensin converting enzyme inhibitors' : ['captopril', 'enalapril' , 'fosinopril', 'lisinopril', 'perindopril', 'quinapril', 'ramipril', 'trandolapril' ], 
		'angiotensin-2 receptor antagonists' : ['candesartan', 'eprosartan', 'irbesartan', 'losartan', 'telmisartan' ],
		'calcium channel blockers - dihydropyridine' : ['amlodipine', 'felodipine', 'lercanidipine', 'nifedipine', 'nimodipine' ],
		'calcium channel blockers - benzothiazepine' : ['diltiazem'],
		'calcium channel blockers - phenylalkylamine' : ['verapamil'], 
		'vasodilators' : ['diazoxide', 'hydralazine', 'minoxidil', 'sodium nitroprusside' ],
		'centrally acting antihypertensives' : ['clonidine', 'methyldopa'],
		'nonselective alpha-blockers' : ['pnehnoxybenzamine', 'phentolamine' ], 
		'selective alpha-blockers' : ['doxazosin', 'prazosin', 'tamsulosin', 'terazosin' ] }

		self.drugs_affecting_heart_rhythm =  { 'antiarrhythmics' : ['adenosine', 'amiodarone', 'digoxin', 'disopyramide', 'esmolol', 'flecainide', 'lignocaine', 'mexiletine', 'procaineamide', 'quinidine', 'sotalol', 'verapamil' ],
		'anti-bradyarrhythmics' : ['atropine', 'isoprenaline'] }
		self.drugs_for_dyslipidemia = { 'hmg-CoA reductase inhibitors' : ['atorvastatin', 'fluvastatin', 'pravastatin', 'simvastatin' ],
		'bile acid binding resins' : ['cholestyramine', 'colestipol'],
		'dyslipidemia drugs - other' : ['gemfibrozil', 'nicotinic acid' ] }
		self.drugs_for_peripheral_vascular_disease = { 
		'peripheral vascular disease drugs' : ['hydroxyethylrutosides',
		'oxpentifylline', 'sodium tetradecyl sulfate' ] }

		self.anticoagulants = { 'heparins' : ['dalteparin', 'danaparoid', 'enoxaparin', 'standard heparin'], 
		'oral anticoagulants' :[ 'warfarin', 'phenindione' ],
		'hirudins' : ['desirudin'],
		'antiplatelets' : ['aspirin', 'dipyrdamole'],
		'antiplatelets - platelet glycoprotein 3b/3a receptor blockers' :['abciximab', 'tirofiban'],
		'antiplatelets - thienopyridines' : ['clopidogrel' , 'ticlopidine' ], 
		'thrombolytics' : ['altepase', 'reteplase', 'streptokinase', 'tenecteplase' ] }
		self.haemostatics = { 
		'haemostatics'  : ['factor VIII', 'factor IX', 'antithrombin III', 'protamine', 'tranexamic acid', 'vitamin K1' ] }
		self.haemopoietics = { 'haemopoietics' : ['epoetin alfa'] }
		self.haematinics = { 'haematinics': ['folic acid', 'iron', 'vitamin B12' ] }
		self.topical_corticosteroids = { 'topical corticosteroids - mild' : ['hydrocortisone', 'hydrocortisone acetate'] , 'topical corticosteroids - moderate' : [ 'betamethasone valerate', 'triamcinolone acetonide', 'alclometasone diproprionate' ], 'topical corticosteroids - potent' : ['betamethasone dipropionate', 'betamethasone valerate 0.1%', 'desonide', 'memtasone furoate', 'methylprednisolone aceponate' ], 'topical corticosteroids - very potent' : ['betamethasone dipropionate in optimised propylene glycol' ] }
		self.tars = { 'tars': [ 'coal tar', 'ichthammol', 'wood tar'] }
		self.acne_drugs = { 
		'acne - keratolytics': ['azelaic acid', 'benzoyl peroxide' ], 
		'acne - topical antibacterials' : ['clindamycin', 'erythromycin' ], 'oral retinoids': ['actretin', 'isotretinoin'], 
		'acne - topical retinoids': ['adapalene', 'isotretinoin topical', 'tretinoin' ] }
		
		self.anti_dermatophytic = {
		'topical antifungals - imidazoles' : ['bifonazole', 
		'clotrimazole', 'econazole', 'ketoconazole', 'miconazole'],
		'topical antifungals - other' : ['amorolfine', 'nystatin', 'terbinafine', 'tolnaftate' ]  }
	
	
		self.pediculicides = {
		'scabicides and pediculicides' : ['benzyl benzoate', 'crotamiton', 'maldison', 'permethrin' ,'pyrethrins with piperonyl butoxide']
		}
		self.dermatological_antiinfectives = {
		'antibacterials - topical' : ['metronidazole', 'mupirocin', 'neomycin' ],
		'antiviral - topical' : ['aciclovir', 'idoxuridine'] 
		}

		self.antidepressants = {
		'antidepressants - tricyclic': ['amitriptyline', 'clomipramine', 'dothiepin', 'doxepin', 'imipramine', 'nortriptyline', 'trimipramine', 'mianserin'], 'monoamine oxidase inhibitors': [ 'phenelzine', 'tranylcypromine'] , 
		'reversible inhibitors of monoamine oxidase A' : ['moclobemide'], 
		'selective serotonin reuptake inhibitors (SSRIs)' : ['citalopram', 'fuoxetine', 'fluvoxamine', 'paroxetine', 'sertraline' ],
		'antidepressants - other' : ['mirtazapine', 'nefazodone', 'venlafaxine'] }
		self.antipsychotics = {
		'antipsychotics - conventional': ['chlorpromazine', 'droperidol', 'haloperidol', 'pericyazine', 'pimozide', 'thioridazine' , 'thiothixene', 'trifluoperazine', 'zuclopenthixol acetate', 'zuclopenthixol dihydrochloride', 'flupenthixol decanoate', 'fluphenazine decanoate', 'haloperidol decanoate', 'zuclopenthixol deconoate' ],
		'antipsychotics - atypical' : ['clozapine', 'olanzapine', 'quetiapine', 'risperidone'],
		'bipolar disorder drugs' : ['lithium']
		}
		self.anxiolytics = {
		'anxiolytics' : ['alprazolam', 'bromazepam', 'clobazam', 'clonazepam', 'diazepam', 'flunitrazepam', 'lorazepam','midazolam','nitrazepam', 'oxazepam', 'temazepam', 'triazolam' ] ,
		'other anxiolytics' : ['buspirone', 'zolpidem', 'zopiclone'], 
		
		}
		
		self.hyperactivity_drugs = { 
		'attention deficit hyperactivity disorder drugs': [
		'dexamphetamine', 'methylphenidate']
		}
		self.dependence_treatment_drugs = {
		'alcohol dependence treatment': ['acamprosate', 'disulfiram', 'naltrexone' ], 
		'nicotine dependence drugs' : ['nicotine replacement', 'bupropion' ],
		'opioid dependence drugs' : ['buprenorphine', 'methadone', 'naltrexone' ]
		}
		self.respiratory_drugs = {
		'bronchodilators - short acting beta2 agonists': ['fenoterol', 
		'orciprenaline', 'salbutamol', 'terbutaline'],
		'bronchodilators - long acting beta2 agonists': [
		'eformoterol', 'salmeterol'],
		'bronchodilators - anticholinergic drugs': 
			['ipratropium'],
		'respiratory drugs - theophylline derivatives':
			['aminophylline', 'choline theophyllinate', 'theophylline'],
		'corticosteroids - inhaled': 
			['beclomethasone', 'budesonide', 'fluticasone'],
		'respiratory drugs - other anti-inflammatory preventers' :
			['cromoglycate', 'nedocromil'],
		'leuokotriene-receptor antagonists' : 
			['montelukast', 'zafirlukast'],
		'mucolytics' : ['acetylcysteine', 'bromhexine', 'dornase alfa'],
		'pulmonary surfactants' : ['beractant', 'colfosceril'],
		'respiratory stimulants': ['doxapram'],
		'cough suppressants' : ['codeine', 'dihydrocodeine', 'dextromethorphan', 'pholcodine'] }
		self.vaccines = {
		'vaccines - routine': ['bacillus calmette-guerin vaccine',
		'diphtheria-tetanus-pertussis vaccine',
		'diphtheria-tetanus-pertussis-hepatitis B vaccine',
		'adult dphtheria-tetanus vaccine',
		'haemophilus influenzae type B vaccine',
		'haemophlius influenzae type B - hepatitis B vaccine',
		'hepatitis B vaccine',
		'influenza vaccine',
		'measles-mumps-rubella vaccine',
		'pneumococcus vaccine',
		'poliomyelitis vaccine'] , 
		'vaccines - other' : 
			['child diphtheria-tetanus vaccine',
			'cholera vaccine', 
			'diptheria (child} vaccine',
			'diphtheria (adult) vaccine',
			'hepatitis A vaccine',
			'hepatitis B vaccine',
			'hepatitis A + B vaccine',
			'japanese Encephalitis vaccine',
			'rabies / Australian Bat lyssavirus vaccine',
			'meningococcal polysaccharide group A, C, W135, Y vaccine',
			'meningococcal polysacharide-conjugate group C vaccine',
			'plague vaccine',
			'q fever vaccine',
			'rubella vaccine', 'tetanus toxoid vaccine', 'typhoid vaccine (injection)', 'varicella vaccine', 'yellow fever vaccine' ] }
		self.immunoglobulins = {
		'immunoglobulins - normal': ['normal human immunoglobulin'],
		'immunoglobulins - specific' :['cytomegalovirus (CMV) immunoglobulin',
			'hepatitis B (HBIG) immunoglobulin',
			'rabies (RIG) immunoglobulin',
			'anti-Rh D immunoglobulin',
			'tetanus (TIG) immunoglobulin',
			'tetanus immunoglobulin for treatment',
			'zoster (ZIG) immunoglobulin',
			'diphtheria antitoxin'] 
			}
		self.helicobacter_drugs = {
		'helicobacter pylori eradication - first line':
			['proton pump inhibitor + clarythromycin + amoxycillin',
			'proton pump inhibitor + clarithromycin + metronidazole',
			'ranitidine bismuth citrate + clarithromycin + amoxycillin' ],
		'helicobacter pylori eradication - second line':
			['proton pump inhibitor + amoxycillin + metronidazole',
			'colloidal bismuth subcitrate + metronidazole + tetracycline'],
		'helicobacter pylori eradication - treatment failure' :
			['proton pump inhibitor + colloidal bismuth subcitrate + metronidazole + tetracycline']
			}
		self.ulcer_reflux_drugs = {
		'antacids': [ 'alumnium hydroxide', 'calcium carbonate', 'magnesium salts', 'sodium bicarbonate'],
		'gastric cytoprotective' : ['bismuth subcitrate', 'ranitidine bsimuth citrate', 'sucralfate'], 
		'h2 antagonists' : ['cimetidine', 'famotidine', 'nizatidine', 'ranitidine' ], 
		'proton pump inhibitors' : ['esomeprazole','lansoprazole','omeprazole','pantoprazole', 'rabeprazole'],
		'peptic ulcer drug - prostaglandin analogues':['misoprostol'] 
		}
		self.gastrointestinal_motility = {
		'gastrointestinal  motility stimulants' : 
			['cisapride', 'domperidone', 'metoclopramide'],
		'anticholinergics': ['belladona alkaloids', 'dicyclomine', 'hyoscine butylbromide'],
		'antispasmodics': ['alverine', 'mebeverine', 'peppermint oil'],
		}
		self.anti_emetics = {
		'nausea and vomiting drugs - dopamine antagonists':
			['domperidone', 'droperidol', 'haloperidol', 'metoclopramide', 'prochlorperazine'],
		'nausea and vomiting drugs - antihistamines': 
			['dimenhydrinate' , 'promethazine'],
		'nausea and vomiting drugs - anticholinergics': 
			['hyoscine hydrobromide'],
		'nausea and vomiting drugs - 5HT3 antagonisits':
			['dolasetron', 'ondansetron', 'tropisetron'] }
		
		self.laxatives = {
		'laxatives - bulking agents': ['ispaghula husk', 'methylcellulose', 'psyllium', 'sterculia' ],
		'laxatives - stool softeners': ['docusate', 'liquid paraffin', 'poloxamer' ],
		'laxatives - stimulants': ['bisacodyl', 'senna'],
		'laxatives - osmotic' : ['glycerol', 'lactulose', 'sorbitol'],
		'laxatives - saline' : ['sodium salts ( citrate, phosphate, sulfate) ', 'polyethylene glycol (PEG)  electrolyte solution', 'magnesium salts 9carbonate, citrate, hydroxide, sulfate)']
		}
		self.antidiarrhoeals = {
		'oral rehydration salts' : ['tablet/100ml -sodium chloride 117mg , potassium chloride 186mg, glucose 1.62 g, sodium acid citrate 384mg',
		'sachet/200ml - sodium chloride 470mg , potassium chloride 300mg, glucose 3.56g, sodium acid citrate 530mg' ],
		'opioid antidiarrhoeals' : ['codeine', 'diphenoxylate', 'loperamide'] 
		}
		self.inflammatory_bowel_disease_drugs = {
		'inflammatory bowel disease - corticosteroids' : ['budesonide(controlled release capsules)', 'hydrocortisone (foam rectal enema)', 'prednisolone (tablet, enema, suppository)'],
		'inflammatory bowel disease :  5-aminosalicylic acid derivatives': ['mesalazine', 'olsalazine', 'sulfasalazine'] }



		self.antibiotics = {
		'penicillins': [ 'penicillin' , 'amoxicillin', 'flucloxicillin', 'cloxicillin', 'dicloxicillin', 'benzyl-penicillin', 'phenoxymethylpenicillin', 'amoxicillin and clavulanic acid' , 'procaine penicillin', 'piperacillin', 'piperacillin with tazobactam', 'ticarcillin with clavulanic acid'],
		'carbapenems' : [ 'imipenem', 'meropenem' ],
		'monobactams' : [ 'aztreonam' ],
		'aminoglycosides' : [ 'amikacin', 'gentamycin', 'neomycin', 'netilmicin', 'paromomycin', 'tobramycin', 'streptomycin'],
		'lincosamides' : ['clindamycin', 'lincomycin' ],
		'glycopeptides' : ['teicoplanin', 'vancomycin' ],
		'antileprotics' : ['dapsone', 'clofazimine'],
		
		'macrolides' : [ 'erythromycin', 'clarithromycin', 'roxithromycin', 'azithromycin' ], 
		'sulfonamides and trimethoprim' : ['sulfadiazine', 'trimethoprim', 'trimethoprim with sulfamethoxazole'], 
		'tetracyclines' : ['demeclocycline', 'doxycycline', 'minocycline', 'tetracycline' ], 
		'nitroimidazoles' : ['metronidazole', 'tinidazole'],
		
		'cephalosporins first gen' : ['cephalexin', 'cephalothin','cephazolin'], 
		'cephalosporin with anti-haemophilus activity' : [ 'cefaclor', 'cefuroxime', 'cephamandole' ], 
		'cephalosporin , moderate activity, anti-anaerobic' : ['cefotetan', 'cefoxitin' ] , 
		'cephalosporin , broad spectrum ' : ['cefotaxime', 'ceftriaxone'], 
		'cepahlosporin broad spectrum anti-pseudomomal' : [ 'ceftazidime', 'cefepime', 'cefpirome' ] , 
		'quinolones': ['ciprofloxacin', 'norfloxacin', 'gatifloxacin', 'moxifloxacin', 'ofloxacin' ], 
		'anti-mycobacteriums' : ['streptomycin', 'pyrazinamide', 'isoniazid', 'ethambutol', 'cylcoserine', 'capreomycin' ], 
		'anti-bacterials , other' : ['chloramphenicol', 'hexamine hippurate', 'nitrofurantoin',  'spectinomycin', 'linezolid', 'quinupristin with dalfopristin', 'sodium fusidate' ],
		'antifungals, polyenes' : ['amphotericin', 'amphotericin, liposomal', 'nystatin'],
		'antifungals, imidazoles' : ['ketoconazole', 'miconazole'],
		'antifungals, triazoles' : ['fluconazole', 'itraconazole'],
		'antifungals, other' : ['caspofungin', 'flucystosine', 'griseofulvin', 'terbinafine' ],
		'antivirals, guanine analogues' : ['aciclovir', 'famciclovir', 'ganciclovir', 'valaciclovir' ] ,
		'antivirals, nucleoside analogue, reverse transcriptase inhibitors' : ['abacavir', 'didanosine', 'lamivudine', 'stavudine', 'zalcitabine', 'zidovudine' ], 
		'antivirals, non-nucleoside reverse transcriptase inhibitors' : ['delavirdine', 'efavirenz', 'nevirapine'],
		'antivirals, protease inhibitors' : ['amprenavir', 'indinavir', 'lopinavir with ritonavir', 'nelfinavir', 'ritonavir', 'saquinavir' ] ,
		'antivirals, other antivirals' : ['cidofovir', 'foscarnet', 'oseltamivir', 'palivizumab', 'ribavirin', 'zanamivir'],
		'antiprotozoals, antimalarials' : ['atovaquone with proguanil', 'chloroquine', 'doxycycline', 'mefloquine', 'primaquine', 'proguanil', 'pyrimethamine with sulfadoxine', 'quinine' ],
		'antihelmintics' : [ 'ivermectin', 'praziquantel', 'pyrantel', 'albendazole', 'mebendazole', 'thiabendazole' ]
		 
		 }		
		
		self.all_drugs =[ 
		
			self.antibiotics ,
			self.inflammatory_bowel_disease_drugs, 
			self.antidiarrhoeals,  
			self.laxatives, 
			self.anti_emetics,
			 self.gastrointestinal_motility,
			 self.ulcer_reflux_drugs,
			 self.helicobacter_drugs,
			  self.vaccines,
			   self.respiratory_drugs,
			   self.dependence_treatment_drugs,
			   self.hyperactivity_drugs ,
			   self.anxiolytics,
			   self.antipsychotics,
			   self.antidepressants,
			    self.pediculicides ,
			    self.anti_dermatophytic,
			    self.acne_drugs ,
			     self.tars ,
			      self.topical_corticosteroids,
			       self.haematinics,
			        self.haemopoietics,
				 self.haemostatics,
				 self.anticoagulants,
				 self.drugs_for_peripheral_vascular_disease,
				 self.drugs_for_dyslipidemia,
				 self.drugs_affecting_heart_rhythm ,
				  self.hypertension_drugs ,
				  self.angina_drugs 
				  ]

	
		
		



class patient_model:
			

	def __init__(self):
		self.__init_data()
		self.script_model = script_model()
		self.problems_model = problems_model()
		self.drug_model = drug_model()
		self.all_drug_map = None

	def __init_data(self):
		self.selected_drug = None
		self.current_drug_class = None
		self.allergy_list = []
	
	
	def get_drugclass_flat_map(self):
		if self.all_drug_map == None:
			map = {}
			for x in self.drug_model.all_drugs:
				for k,v in x.items():
					map[k] = v
			self.all_drug_map = map
			
		return self.all_drug_map
	

	def get_drug_allergy_list( self, prefix = ""):
		if self.current_drug_class == None:
			return self.get_all_drugs()
		
		return self.get_drugs_for_class( self.current_drug_class)
	
	def get_all_drugs(self):
		list = []
		for k,v in self.get_drugclass_flat_map().items():
			for x in v:
				list.append(x)
		list.sort()		
		return list	

	def get_drug_classes(self, alphabetic = 1):
		list = []
		list.extend( self.get_drugclass_flat_map().keys())
		if alphabetic:
	 		list.sort()
		return list	

	def add_drug_allergy_list( self, drug):
		if not drug in self.drug_allergy_list:
			self.drug_allergy_list.append(drug)

		
	def get_class_for_drug(self, drug):
		for k , v in self.get_drugclass_flat_map().items():
			if drug in v:
				return k
		return None
	
	def get_drugs_for_class( self, aclass):
		list = []
		list.extend( self.get_drugclass_flat_map().get(aclass, []))
		return list

	def set_selected_drug( self, drug):
		self.selected_drug = drug
		self.set_current_drug_class()
	
	def set_current_drug_class(self):
		if self.selected_drug <> None:
			self.current_drug_class = self.get_class_for_drug(drug)
	def get_current_drug_class(self):
		return self.current_drug_class

	def get_allergy_list( self):
		return self.allergy_list

	def add_allergy(self, allergy):
		"""adds a map containing elements for a new allergy. returns a map of
		the old element if one existed, or an empty map if this is a new element"""
		list = [ allergy['key'], allergy.get('date_recorded', ''), allergy['allergy_drug'], allergy['allergy_class'], allergy['drug_reaction'] ]
		s = filter( lambda x: x[2] == list[2], self.allergy_list)
		for x in s:
			self.allergy_list.remove(x)
		old_map = {}
		headings = ( 'key', 'date_recorded', 'allergy_drug', 'allergy_class', 'drug_reaction' )
		for x in s:
			for i in xrange(0,len(x)):
				old_map[headings[i]] = x[i]
	
		self.allergy_list.append(list)
		return old_map
	
	def get_allergies( self, keyList = [] ):
		return filter( lambda x: keyList == [] or x[0] in keyList , self.allergy_list)
	
	def remove_allergies( self, keyList):
		self.allergy_list = filter( lambda x: not x[0] in keyList, self.allergy_list)
		
	def is_drug_in_class( self, drug, aclass):
		if aclass <> self.get_class_for_drug(drug) and aclass == None:
			return 0
		if aclass == None or aclass == '':
			return 1

		if drug in self.get_drugs_for_class(aclass):  
			return 1
		
		return 0
				


	
				
	
	
