#!/usr/bin/perl
use strict;
use warnings;
use File::Temp 'tempfile';
use CGI;
use Text::CSV; # non-core dependency, install from CPAN
use CGI::Carp 'fatalsToBrowser';
use Data::Dumper;

# you may need to update these two values to reflect your system's path structure
my $CITES_db = '/Library/WebServer/CGI-Executables/CITES_db.csv';
my $exe      = '/Library/WebServer/CGI-Executables/HTS-barcode-checker';

# instantiate the CGI parameters parser
my $cgi      = CGI->new;

# need to have this required param, otherwise print start page
if ( my $local_input_file = $cgi->param('input_file') ) {

	# this will hold the command line arguments, the output file is stdout
	my %args = ( 
		'output_file' => '-',
		'CITES_db'    => $CITES_db,
		'logging'     => 'critical',
	);
	
	# get the local temp file name, register for cleanup	
	$args{'input_file'} = write_tmp_file($cgi->upload('input_file'));
	my @cleanup = ( $args{'input_file'} );
	
	# optional: user provided their own csv
	if ( my $local_CITES_db = $cgi->param('CITES_db') ) {
		$args{'CITES_db'} = write_tmp_file($cgi->upload('CITES_db'));
		push @cleanup, $args{'CITES_db'};
	}
	
	# get the other parameters
	my @params = grep { $_ !~ /(?:input_file|CITES_db)/ } $cgi->param;
	for my $p ( @params ) {
		$args{$p} = $cgi->param($p);				
	} 
		
	# make the invocation
	my $command = $exe . ' --avoid_download';
	for my $argname ( keys %args ) {
		$command .= ' --' . $argname . ' ' . $args{$argname};
	}
	my $result = `$command`;
	
	# print the result, clean up
	print_csv($result);
	unlink @cleanup;
}
else {
	print $cgi->header;
	print $_ while <DATA>;
}

sub write_tmp_file {
	my $rfh = shift;
	my ( $wfh, $name ) = tempfile();
	print $wfh $_ while <$rfh>;
	return $name;
}

# write the output
sub print_csv {
	my $string = shift;
	print $cgi->header;
	
	# print the page header. prettify me
	print <<'HEADER';
<html>
<head>
<title>HTS barcode checker - results</title>
<script type="text/javascript" src="http://www.kryogenix.org/code/browser/sorttable/sorttable.js"></script>
<style type="text/css">
	td, th { 
		vertical-align: top;
		font-family: verdana;
		font-size: 12px;
		text-align: left
	}
	th {
	    background-color:#eee;
    	cursor: pointer
	}
	td.hit, td.info {
		width: 30%
	}
	td.nowrap {
		white-space: nowrap
	}
	tr.cites {
		background-color: yellow
	}
</style>
<head>
<body>
HEADER

	# open string handle for CSV parser
	open my $fh, '<', \$string or die $!;
	my $csv = Text::CSV->new; 

	# print table header
	print '<table class="sortable">';	
	
	# iterate over rows
	my $colnames = $csv->getline($fh);
	my %header;
	$header{$colnames->[$_]} = $_ for 0 .. $#{ $colnames };
	my @header = qw(query hit identity length e-value bit-score species info appendix);
	print '<tr>';
	print map { "<th>$_</th>" } @header;
	print '</tr>', "\n";
	
	ROW: while ( my $row = $csv->getline($fh) ) {
		next ROW if not $row->[0]; 
		if ( $row->[-1] =~ /^\d$/ ) {
			print '<tr class="cites">';
		}
		else {
			print '<tr>';
		}
		my $taxonID;
		COL: for my $i ( 0 .. $#{ $colnames } ) {
			next COL if $colnames->[$i] eq 'accession';
			next COL if $colnames->[$i] eq 'NCBI Taxonomy name';
			next COL if $colnames->[$i] eq 'taxon id' and $taxonID = $row->[$i];			
		
			# capture the gi, write the definition line
			if ( $row->[$i] and $row->[$i] =~ /^gi\|(\d+)\|[a-z]+\|\S+\| (.+)$/ ) {
				my ( $gi, $desc ) = ( $1, $2 );
				print "<td class='hit'><a href='http://ncbi.nlm.nih.gov/nuccore/$gi'>$desc</a></td>"; 
			}
			
			# write the species with a link to NCBI taxonomy
			elsif ( $colnames->[$i] eq 'species' ) {
				my $name = $row->[$i];
				print "<td class='nowrap'><a href='http://ncbi.nlm.nih.gov/taxonomy/$taxonID'>$name</a></td>"; 			
			}
			
			# capture the footnote
			elsif ( $colnames->[$i] =~ /CITES/ ) {
				my $text = $row->[$i] || '';
				print "<td class='info'>$text</td>";
			}
			
			# do the rest
			else {
				print '<td class="nowrap">', $row->[$i] || '', '</td>';
			}
		}
		print '</tr>', "\n";
	}

	# print html footer	
	print '</table></body></html>';
		
}

__DATA__
<html>
	<head>
		<title>HTS barcode checker</title>
		<script type="text/javascript">
			// expands the advanced options
			function expander() {
				var advancedDiv = document.getElementById('advanced');
				var advancedLink = document.getElementById('expander');
				var display = advancedDiv.style.display;
				if ( display == 'none' || display == '' ) {
					advancedDiv.style.display = 'block';
					advancedLink.innerHTML = '- Hide advanced options';
				}
				else {
					advancedDiv.style.display = 'none';
					advancedLink.innerHTML = '+ Show advanced options';				
				}
			}
			
			// warns before submitting
			function submitWarn() {
				alert(
					"About to BLAST your sequences. " +
					"Click to continue and wait for the process to complete. " +
					"Do NOT close your browser window."
				);
				document.getElementById('waiting').style.display = 'block';
			}
		</script>
		<style type="text/css">
			#expander { 
				text-decoration: none; 
				display: block; 
				clear: left; 
				text-align: center		
			}
			#advanced { display: none }
			body { 
				font-family: verdana, arial, sans-serif;
				font-size: 10px
			}
			label { 
				display: block; 
				float: left; 
				width: 200px;
				text-align: right;
				clear: left;
				padding-right: 10px
			}
			input { display: block; float: left }
			select { width: 200px; display: block }
			h1 { text-align: center }
			body {
				margin:50px 0px; 
				padding:0px;
				text-align:center;
			}			
			.waiting {
				width: 220px;
				text-align: center;
				left: 50%;
				width: 220px;
				margin-top: 35px;
				margin-left: -110px;				
				position: absolute;
				z-index: 1;
				display: none
			}
			form { 
				width: 500px; 
				margin: 0px auto; 
				text-align: left 
			}
		</style>		
	</head>	
	<body>	
		<img class="waiting" id="waiting" src="http://tweetreach.com/images/wait.gif" />		
		<form 
			id="form"
			action="/cgi-bin/HTS-barcode-checker.cgi" 
			method="POST"
			enctype="multipart/form-data">
			
			<h1>HTS barcode checker</h1>

			<!-- advanced options, normally hidden -->
			<a id="expander" onClick="expander()" href='#'>+ Show advanced options</a>
			<br />
			
			<label for="input_file">Input file 
				(<a href="https://raw.github.com/naturalis/HTS-barcode-checker/master/data/Test_data.fasta">example</a>)
			</label>
			<input type="file" name="input_file" id="input_file"/><br />
						
			<div id="advanced">
			
				<label for="CITES_db">CITES database file</label>
				<input type="file" name="CITES_db" id="CITES_db"/><br /><br />
						
				<label for="BLAST_algorithm">BLAST algorithm</label>
				<select name="BLAST_algorithm" id="BLAST_algorithm">
					<option value="blastn" selected="selected">blastn</option>
					<option value="blastp">blastp</option>
					<option value="blastx">blastx</option>
					<option value="tblastn">tblastn</option>
					<option value="tblastx">tblastx</option>
				</select>
		
				<label for="BLAST_database">BLAST database</label>
				<select name="BLAST_database" id="BLAST_database">
					<option value="nt" selected="selected">Nucleotide collection</option>
					<option value="refseq_rna">Reference RNA sequences</option>
					<option value="refseq_genomic">Reference genomic sequences</option>
					<option value="chromosome">NCBI Genomes</option>
					<option value="est">Expressed sequence tags</option>
					<option value="gss">Genomic survey sequences</option>
					<option value="HTGS">High throughput genomic sequences</option>
					<option value="pat">Patent sequences</option>
					<option value="pdb">Protein Data Bank</option>
					<option value="alu_repeats">Human ALU repeat elements</option>
					<option value="dbsts">Sequence tagged sites</option>
					<option value="wgs">Whole-genome shotgun contigs</option>
					<option value="TSA">Transcriptome Shotgun Assembly</option>
				</select>
			
				<label for="megablast">Use megablast</label>
				<input type="checkbox" name="megablast" value="megablast" id="megablast"/>

				<label for="hitlist_size">Number of returned results</label>
				<input type="text" name="hitlist_size" id="hitlist_size" value="10"/>

		
				<label for="min_identity">Minimum sequence identity</label>
				<input type="text" name="min_identity" value="97" id="min_identity"/>
		
				<label for="min_coverage">Minimum coverage</label>
				<input type="text" name="min_coverage" value="100" id="min_coverage"/>		

				<label for="max_evalue">Maximum e-value</label>
				<input type="text" name="max_evalue" value="0.05" id="max_evalue"/>		
			
			</div>
			<label for="submit">Submit</label>
			<input type="submit" id="submit" onClick="submitWarn()" />			
		</form>
	</body>
</html>